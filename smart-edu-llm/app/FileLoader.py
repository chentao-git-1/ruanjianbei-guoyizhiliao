import os
from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader, UnstructuredPDFLoader, \
    TextLoader
from langchain_core.document_loaders import BaseLoader


class LoaderFactory:
    @staticmethod
    def get_loader(file_path: str | Path) -> BaseLoader:
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ['.txt', '.md']:
            return TextLoader(file_path, encoding='utf-8')
        elif ext == '.pdf':
            return UnstructuredPDFLoader(file_path)
        elif ext in ['.ppt', '.pptx']:
            return UnstructuredPowerPointLoader(file_path, mode='elements')
        elif ext in ['.docx', '.doc']:
            try:
                return UnstructuredWordDocumentLoader(file_path)
            except Exception:
                return Docx2txtLoader(file_path)
        else:
            raise ValueError(f'Unsupported file type {ext}')