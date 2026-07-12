from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QSpinBox
)

from pdf_engine import PdfEngine


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.engine = PdfEngine()
        self.document = None

        self.setWindowTitle("PDF Translator")
        self.resize(1100, 800)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        row = QHBoxLayout()
        row.addWidget(QLabel("PDF"))

        self.edFile = QLineEdit()
        self.edFile.setReadOnly(True)
        row.addWidget(self.edFile)

        self.btnOpen = QPushButton("Выбрать PDF")
        self.btnOpen.clicked.connect(self.open_pdf)
        row.addWidget(self.btnOpen)

        layout.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Страница"))

        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(1)
        row2.addWidget(self.spin)

        self.btnBlocks = QPushButton("Показать блоки")
        self.btnBlocks.clicked.connect(self.show_blocks)
        self.btnBlocks.setEnabled(False)
        row2.addWidget(self.btnBlocks)

        self.btnInspect = QPushButton("Свойства")
        self.btnInspect.setEnabled(False)
        self.btnInspect.clicked.connect(self.inspect_block)
        row2.addWidget(self.btnInspect)

        row2.addStretch()

        layout.addLayout(row2)

        layout.addWidget(QLabel("Информация"))
        self.info = QTextEdit()
        self.info.setMaximumHeight(180)
        self.info.setReadOnly(True)
        layout.addWidget(self.info)

        layout.addWidget(QLabel("Блоки"))
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def open_pdf(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите PDF", "", "PDF (*.pdf)"
        )
        if not filename:
            return

        self.document = self.engine.load(filename)

        self.edFile.setText(filename)
        self.spin.setMaximum(self.document.page_count)
        self.btnBlocks.setEnabled(True)
        self.btnInspect.setEnabled(True)

        pages_with_text = sum(1 for p in self.document.pages if p.blocks)
        empty_pages = self.document.page_count - pages_with_text
        size_mb = self.document.file_size / 1024 / 1024

        self.info.clear()
        self.info.append("Документ")
        self.info.append("")
        self.info.append(Path(filename).name)
        self.info.append("")
        self.info.append(f"Размер              : {size_mb:.2f} МБ")
        self.info.append(f"Страниц             : {self.document.page_count}")
        self.info.append("")
        self.info.append(f"Текстовых страниц   : {pages_with_text}")
        self.info.append(f"Без текста          : {empty_pages}")
        self.info.append("")
        self.info.append(f"Оглавление          : {'Да' if self.document.has_toc else 'Нет'}")
        self.info.append(f"Ссылки              : {'Да' if self.document.has_links else 'Нет'}")

        self.text.clear()

    def show_blocks(self):
        if self.document is None:
            return

        page = self.document.pages[self.spin.value() - 1]
        self.current_page = page

        self.text.clear()

        for block in page.blocks:
            self.text.append("=" * 70)
            self.text.append(f"Блок {block.number}")
            self.text.append(f"Координаты: {block.bbox}")
            self.text.append("")
            self.text.append(block.text)
            self.text.append("")

    def inspect_block(self):

        if not hasattr(self, "current_page"):
            self.info.append("")
            self.info.append("Сначала нажмите 'Показать блоки'.")
            return

        self.info.append("")
        self.info.append(f"Страница содержит {len(self.current_page.blocks)} блоков.")
        if not self.current_page.blocks:
            return

        block = self.current_page.blocks[0]

        self.info.append("")
        self.info.append("Первый блок")
        self.info.append(f"Номер : {block.number}")
        self.info.append(f"BBox  : {block.bbox}")

        if block.lines and block.lines[0].spans:

            span = block.lines[0].spans[0]

            self.info.append("")
            self.info.append(f"Шрифт : {span.font}")
            self.info.append(f"Размер: {span.size}")
            self.info.append(f"Flags : {span.flags}")
            self.info.append(f"Origin: {getattr(span, 'origin', 'НЕТ')}")
            self.info.append(f"Asc   : {getattr(span, 'ascender', 'НЕТ')}")
            self.info.append(f"Desc  : {getattr(span, 'descender', 'НЕТ')}")
