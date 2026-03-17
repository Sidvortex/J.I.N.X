"""
AGENT.PY — AI AGENT MODULE
Handles: Document Q&A (RAG over uploaded PDFs/docs), code review,
         image search for visual answers, reading documents aloud,
         and laptop integration for live code watching.

Upload documents to data/documents/
Set WATCH_CODE_DIR in dna.py to enable live code review.
"""

import os
import json
import time
import threading
import hashlib
from pathlib import Path
from datetime import datetime

import dna
from blackbox import Blackbox
from synapse  import Synapse
from psyche   import Psyche

# Optional imports
try:
    import google.generativeai as genai
    genai.configure(api_key=dna.GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-2.0-flash")
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pypdf as PyPDF2
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
        print("  [AGENT] Install PyPDF2 or pypdf for PDF support: pip install pypdf")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class Agent:
    def __init__(self, synapse: Synapse, blackbox: Blackbox, psyche: Psyche):
        self.synapse   = synapse
        self.blackbox  = blackbox
        self.psyche    = psyche
        self.running   = False

        # Document store: {filename: {"text": str, "hash": str}}
        self.document_store = {}

        # Code watch state
        self.watched_files = {}  # {path: last_hash}
        self.code_review_queue = []

        # Load existing documents
        self._load_documents()

        # Subscribe to MQTT commands
        synapse.subscribe(dna.TOPIC["command"], self._on_command)
        synapse.subscribe(dna.TOPIC["web_command"], self._on_web_command)

        print(f"  [AGENT] Loaded {len(self.document_store)} documents")
        if dna.WATCH_CODE_DIR:
            print(f"  [AGENT] Watching code: {dna.WATCH_CODE_DIR}")

    # ── Document Loading ───────────────────────────────────────────────────

    def _load_documents(self):
        """Load all documents from the documents directory."""
        doc_dir = Path(dna.DOCUMENTS_DIR)
        if not doc_dir.exists():
            doc_dir.mkdir(parents=True)
            return

        for path in doc_dir.iterdir():
            if path.suffix.lower() in {".pdf", ".txt", ".md", ".py", ".js", ".docx"}:
                self._index_document(path)

    def _index_document(self, path: Path) -> bool:
        """Extract and index text from a document."""
        try:
            text = self._extract_text(path)
            if not text:
                return False
            doc_hash = hashlib.md5(text.encode()).hexdigest()

            # Skip if already indexed with same content
            existing = self.document_store.get(path.name, {})
            if existing.get("hash") == doc_hash:
                return True

            self.document_store[path.name] = {
                "text": text,
                "hash": doc_hash,
                "path": str(path),
                "indexed_at": datetime.now().isoformat(),
                "size": len(text),
            }
            print(f"  [AGENT] Indexed: {path.name} ({len(text)} chars)")
            return True
        except Exception as e:
            print(f"  [AGENT] Failed to index {path.name}: {e}")
            return False

    def _extract_text(self, path: Path) -> str:
        """Extract plain text from various file formats."""
        ext = path.suffix.lower()

        if ext == ".pdf" and PDF_AVAILABLE:
            return self._extract_pdf(path)

        elif ext == ".docx" and DOCX_AVAILABLE:
            doc = docx.Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)

        elif ext in {".txt", ".md", ".py", ".js", ".ts", ".css", ".html", ".java", ".c", ".cpp"}:
            return path.read_text(encoding="utf-8", errors="ignore")

        return ""

    def _extract_pdf(self, path: Path) -> str:
        text_parts = []
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
        except Exception as e:
            print(f"  [AGENT] PDF extraction error: {e}")
        return "\n".join(text_parts)

    def add_document(self, path: str) -> bool:
        """Add a new document to the index."""
        p = Path(path)
        if not p.exists():
            return False
        return self._index_document(p)

    def list_documents(self) -> list:
        return [{"name": k, "size": v["size"]} for k, v in self.document_store.items()]

    # ── Document Q&A ───────────────────────────────────────────────────────

    def query_documents(self, question: str) -> str:
        """Answer a question using the document knowledge base."""
        if not self.document_store:
            return "No documents in my database. Upload some to data/documents/ first."

        if not GEMINI_AVAILABLE:
            return "AI brain offline. Check Gemini API key."

        # Simple RAG: concatenate all document text (trimmed to fit context)
        context_parts = []
        total_chars = 0
        max_chars   = dna.MAX_CONTEXT_TOKENS * 3  # Rough char estimate

        for name, doc in self.document_store.items():
            excerpt = doc["text"][:5000]  # Max 5k chars per doc
            context_parts.append(f"=== {name} ===\n{excerpt}")
            total_chars += len(excerpt)
            if total_chars > max_chars:
                break

        context = "\n\n".join(context_parts)

        prompt = (
            f"{self.psyche.get_system_prompt()}\n\n"
            f"The user has uploaded documents. Use this knowledge to answer:\n\n"
            f"DOCUMENT CONTENT:\n{context}\n\n"
            f"USER QUESTION: {question}\n\n"
            "Answer based on the documents. If the answer isn't in the documents, say so. "
            "Be concise and accurate. No markdown formatting."
        )

        try:
            response = GEMINI_MODEL.generate_content(prompt)
            answer   = response.text.strip()
            self.blackbox.log_event("AGENT_QUERY", {"question": question[:100], "source": "documents"})
            return answer
        except Exception as e:
            return f"I ran into a problem: {e}"

    def read_document_aloud(self, filename: str, vocoder=None) -> str:
        """Read a document summary aloud via vocoder."""
        if filename not in self.document_store:
            # Try partial match
            matches = [k for k in self.document_store if filename.lower() in k.lower()]
            if not matches:
                return f"I don't have a document called {filename}. Available: {', '.join(self.document_store.keys())}"
            filename = matches[0]

        doc_text = self.document_store[filename]["text"]

        # Generate a spoken summary
        prompt = (
            f"Summarize this document for listening (not reading). "
            f"Be clear, natural, and conversational. 3-5 sentences max.\n\n"
            f"Document: {filename}\n\n{doc_text[:3000]}"
        )

        try:
            response = GEMINI_MODEL.generate_content(prompt)
            summary  = response.text.strip()
            if vocoder:
                vocoder.speak(f"Here's a summary of {filename}: {summary}")
            return summary
        except Exception as e:
            return f"Couldn't summarize: {e}"

    # ── Code Review ────────────────────────────────────────────────────────

    def review_code(self, code: str, filename: str = "code", language: str = None) -> str:
        """Review code and return analysis."""
        if not GEMINI_AVAILABLE:
            return "Can't review code — Gemini offline."

        lang = language or self._detect_language(filename)

        prompt = (
            f"{self.psyche.get_system_prompt()}\n\n"
            f"Review this {lang} code. Be the smartest code reviewer in the room:\n\n"
            f"```{lang}\n{code}\n```\n\n"
            "Give feedback on:\n"
            "1. Bugs or errors\n"
            "2. Performance issues\n"
            "3. Security concerns\n"
            "4. Code style and best practices\n"
            "5. Suggested improvements\n\n"
            "Be concise, sharp, and technically accurate. "
            "Keep JINX's sarcastic personality but make the review genuinely useful. "
            "Format as plain text, no markdown."
        )

        try:
            response = GEMINI_MODEL.generate_content(prompt)
            review   = response.text.strip()
            self.blackbox.log_event("CODE_REVIEW", {"file": filename, "lines": code.count("\n")})
            return review
        except Exception as e:
            return f"Code review failed: {e}"

    def fix_code(self, code: str, issue: str = "", language: str = None) -> str:
        """Attempt to fix code issues."""
        if not GEMINI_AVAILABLE:
            return code

        lang = language or "python"
        prompt = (
            f"Fix the following {lang} code. {f'Issue: {issue}' if issue else ''}\n\n"
            f"```{lang}\n{code}\n```\n\n"
            "Return ONLY the fixed code, no explanations, no markdown fences."
        )

        try:
            response = GEMINI_MODEL.generate_content(prompt)
            return response.text.strip().replace(f"```{lang}", "").replace("```", "").strip()
        except Exception:
            return code

    def _detect_language(self, filename: str) -> str:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".c": "c", ".cpp": "cpp", ".cs": "csharp",
            ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
            ".html": "html", ".css": "css", ".sql": "sql",
        }
        ext = Path(filename).suffix.lower()
        return ext_map.get(ext, "code")

    def _watch_code_directory(self):
        """Watch WATCH_CODE_DIR for file changes and auto-review."""
        if not dna.WATCH_CODE_DIR:
            return

        watch_path = Path(dna.WATCH_CODE_DIR)
        if not watch_path.exists():
            print(f"  [AGENT] Watch directory not found: {dna.WATCH_CODE_DIR}")
            return

        code_extensions = {".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rs"}

        while self.running:
            try:
                for file_path in watch_path.rglob("*"):
                    if file_path.suffix.lower() not in code_extensions:
                        continue
                    if file_path.stat().st_mtime < time.time() - 5:
                        continue  # Only check recently modified

                    file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
                    if self.watched_files.get(str(file_path)) != file_hash:
                        self.watched_files[str(file_path)] = file_hash
                        code = file_path.read_text(encoding="utf-8", errors="ignore")
                        if len(code) > 50:  # Skip tiny files
                            review = self.review_code(code, file_path.name)
                            # Publish review to dashboard and notify
                            self.synapse.publish(dna.TOPIC["command"],
                                json.dumps({
                                    "type": "code_review_result",
                                    "file": file_path.name,
                                    "review": review,
                                }))
                            print(f"  [AGENT] Auto-reviewed: {file_path.name}")
            except Exception as e:
                print(f"  [AGENT] Watch error: {e}")
            time.sleep(5)

    # ── MQTT Handlers ─────────────────────────────────────────────────────

    def _on_command(self, payload: str):
        try:
            cmd = json.loads(payload)
            if cmd.get("type") == "agent_query":
                query    = cmd.get("query", "")
                response = self.query_documents(query)
                self.synapse.publish(dna.TOPIC["command"],
                    json.dumps({"type": "agent_response", "response": response}))

            elif cmd.get("type") == "code_review":
                code    = cmd.get("code", "")
                fname   = cmd.get("filename", "code")
                review  = self.review_code(code, fname)
                self.synapse.publish(dna.TOPIC["command"],
                    json.dumps({"type": "code_review_result", "file": fname, "review": review}))

        except (json.JSONDecodeError, KeyError):
            pass

    def _on_web_command(self, payload: str):
        try:
            cmd = json.loads(payload)
            action = cmd.get("action", "")

            if action == "add_document":
                path = cmd.get("path", "")
                success = self.add_document(path)
                result = "indexed" if success else "failed"
                self.synapse.publish(dna.TOPIC["command"],
                    json.dumps({"type": "document_status", "result": result, "path": path}))

            elif action == "list_documents":
                docs = self.list_documents()
                self.synapse.publish(dna.TOPIC["command"],
                    json.dumps({"type": "document_list", "docs": docs}))

            elif action == "query":
                question = cmd.get("question", "")
                response = self.query_documents(question)
                self.synapse.publish(dna.TOPIC["command"],
                    json.dumps({"type": "agent_response", "response": response}))

        except (json.JSONDecodeError, KeyError):
            pass

    # ── Main Loop ─────────────────────────────────────────────────────────

    def run(self):
        self.running = True

        # Start code watcher if configured
        if dna.WATCH_CODE_DIR:
            threading.Thread(target=self._watch_code_directory, daemon=True).start()

        # Watch for new documents
        while self.running:
            self._load_documents()  # Re-scan for new files
            time.sleep(30)

    def stop(self):
        self.running = False
