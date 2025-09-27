"""
Document Management Handler
Handles all document upload and processing functionality.

TODO for team members:
- Implement PDF text extraction using PyPDF2
- Add Word document processing with python-docx
- Implement file validation and error handling
- Add document preview functionality
- Integrate with OCR for scanned documents
"""

import flet as ft
from typing import Any
from pathlib import Path
import shutil
import tempfile

# Optional OCRAgent import (preferred) or fallback to pytesseract
try:
    from app.agents.ocr_agent import OCRAgent
    OCR_AGENT_AVAILABLE = True
except Exception:
    OCR_AGENT_AVAILABLE = False
    try:
        import pytesseract
        from PIL import Image
        OCR_AVAILABLE = True
    except Exception:
        OCR_AVAILABLE = False


class DocumentHandler:
    """Handles document upload and processing operations"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        # TODO: Initialize PDF/DOC processors, file validators, etc.
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt']
    
    def upload_document(self, e: Any = None):
        """
        Handle document file upload
        
        TODO: Implement the following:
        1. Show file picker with supported formats
        2. Validate selected file
        3. Extract text from document
        4. Display extracted text in UI
        5. Save document reference for later use
        """
        # Accept either an event from FilePicker or a direct path
        try:
            file_path = None
            if e is None:
                self._show_message("No file selected", success=False)
                return ""

            # If e has attribute files (FilePicker event)
            if hasattr(e, 'files') and e.files:
                # Flet FilePicker gives a list of files with .path and .name
                file_path = e.files[0].path
            elif isinstance(e, str):
                file_path = e
            elif hasattr(e, 'file'):
                file_path = getattr(e, 'file')

            if not file_path:
                self._show_message("No file selected", success=False)
                return ""

            p = Path(file_path)
            suffix = p.suffix.lower()

            # Determine destination: save raw file into current class folder
            try:
                class_name = current_class if (current_class := getattr(self, 'current_class', None)) else "General"
            except Exception:
                class_name = "General"

            target_dir = Path("data/classes") / class_name / "notes" / "Imported"
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / p.name
            shutil.copy(file_path, target_path)

            extracted_text = ""
            if suffix in ['.txt']:
                extracted_text = target_path.read_text(encoding='utf-8', errors='ignore')
            elif suffix in ['.pdf']:
                # lightweight PDF text extraction using PyPDF2 if available
                try:
                    import PyPDF2
                    with open(target_path, 'rb') as fh:
                        reader = PyPDF2.PdfReader(fh)
                        pages = [pg.extract_text() or "" for pg in reader.pages]
                        extracted_text = "\n\n".join(pages)
                except Exception:
                    extracted_text = ""  # fallback to empty
            elif suffix in ['.docx']:
                try:
                    import docx
                    doc = docx.Document(target_path)
                    extracted_text = "\n\n".join(p.text for p in doc.paragraphs)
                except Exception:
                    extracted_text = ""
            elif suffix in ['.jpg', '.jpeg', '.png']:
                # run OCR via OCRAgent if available, otherwise try pytesseract directly
                if OCR_AGENT_AVAILABLE:
                    try:
                        agent = OCRAgent()
                        extracted_text = agent.run(str(target_path))
                    except Exception:
                        extracted_text = ""
                elif OCR_AVAILABLE:
                    try:
                        img = Image.open(target_path)
                        extracted_text = pytesseract.image_to_string(img)
                    except Exception:
                        extracted_text = ""
                else:
                    extracted_text = ""  # OCR not available in this environment

            # Save extracted text as a .txt next to the imported file for future reference
            try:
                if extracted_text and extracted_text.strip():
                    txt_path = target_path.with_suffix('.txt')
                    txt_path.write_text(extracted_text, encoding='utf-8')
            except Exception:
                pass

            # Update the notes editor value if ref was provided (UI will pass notes_ref)
            # The UI passes notes_ref as second arg in callbacks.get('upload_document')
            # If this handler is called directly, simply return the extracted text
            self._show_message(f"📄 Imported {target_path.name}")
            return extracted_text

        except Exception as exc:
            self._show_message(f"❌ Failed to import document: {exc}", success=False)
            return ""
        
        # Example implementation structure:
        # file_path = self._show_file_picker(self.supported_formats)
        # if file_path:
        #     if self._validate_file(file_path):
        #         text_content = self._extract_text(file_path)
        #         self._display_document_text(text_content)
        #         self._save_document_reference(file_path)
        #         self._show_message(f"✅ Document uploaded: {file_path}")
        #     else:
        #         self._show_message("❌ Unsupported file format", success=False)
    
    def process_document(self, e: Any = None):
        """
        Handle processing uploaded document
        
        TODO: Implement the following:
        1. Apply OCR if needed for scanned documents
        2. Clean and format extracted text
        3. Split into sections/chapters
        4. Generate document summary
        5. Index content for search
        """
        # Placeholder implementation
        self._show_message("⚙️ Process Document - Ready for implementation!")
        
        # Example implementation:
        # current_doc = self._get_current_document()
        # if current_doc:
        #     processed_text = self._process_text(current_doc.content)
        #     sections = self._split_into_sections(processed_text)
        #     summary = self._generate_summary(processed_text)
        #     self._update_document_display(sections, summary)
        #     self._show_message("✅ Document processed successfully")
    
    def clear_document(self, e: Any = None):
        """
        Handle clearing uploaded document
        
        TODO: Implement the following:
        1. Show confirmation dialog
        2. Clear document from memory
        3. Reset document display areas
        4. Clean up temporary files
        5. Show confirmation message
        """
        # Placeholder implementation
        self._show_message("🗑️ Clear Document - Ready for implementation!")
        
        # Example implementation:
        # if self._confirm_clear_document():
        #     self._clear_document_data()
        #     self._reset_document_display()
        #     self._cleanup_temp_files()
        #     self._show_message("✅ Document cleared")
    
    def _show_message(self, message: str, success: bool = True):
        """Helper method to show messages"""
        color = "#66A36C" if success else "#6A2830"
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(message), bgcolor=color)
        )
    
    # TODO: Helper methods for team members to implement
    # def _show_file_picker(self, allowed_extensions: list) -> str:
    #     """Show file picker and return selected file path"""
    #     pass
    # 
    # def _validate_file(self, file_path: str) -> bool:
    #     """Validate file format and size"""
    #     pass
    # 
    # def _extract_text(self, file_path: str) -> str:
    #     """Extract text from PDF/DOC file"""
    #     # For PDF: use PyPDF2 or pdfplumber
    #     # For DOC/DOCX: use python-docx
    #     # For TXT: simple file read
    #     pass
    # 
    # def _display_document_text(self, text: str):
    #     """Display extracted text in UI"""
    #     pass
    # 
    # def _process_text(self, text: str) -> str:
    #     """Clean and process extracted text"""
    #     pass