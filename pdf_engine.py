import fitz
from pathlib import Path


class PdfInfo:

    def __init__(self, filename: str):

        self.filename = Path(filename)

        self.doc = fitz.open(filename)

        self.page_count = len(self.doc)

        self.file_size = self.filename.stat().st_size

    def close(self):

        self.doc.close()

    @property
    def size_mb(self):

        return self.file_size / 1024 / 1024