from pathlib import Path
import fitz


class PdfInfo:

    def __init__(self, filename: str):

        self.filename = Path(filename)

        self.doc = fitz.open(filename)

        self.page_count = self.doc.page_count

        self.file_size = self.filename.stat().st_size

        self.text_pages = 0
        self.empty_pages = 0

        self.has_links = False
        self.has_toc = False

        self.toc = []

        self._analyze()

    # -----------------------------------------------------

    def _analyze(self):

        for page in self.doc:

            text = page.get_text("text").strip()

            if text:
                self.text_pages += 1
            else:
                self.empty_pages += 1

            if page.get_links():
                self.has_links = True

        #
        # Оглавление
        #

        toc = self.doc.get_toc()

        if toc:

            self.has_toc = True

            self.toc = toc

    # -----------------------------------------------------

    @property
    def size_mb(self):

        return self.file_size / 1024 / 1024

    # -----------------------------------------------------

    def first_toc(self, count=10):

        return self.toc[:count]

    # -----------------------------------------------------

    def close(self):

        self.doc.close()