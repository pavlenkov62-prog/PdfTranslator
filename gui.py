from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QSpinBox, QSplitter, QSizePolicy
)

from PySide6.QtGui import QPixmap

from PySide6.QtCore import Qt

from pdf_engine import PdfEngine
from translator import Translator

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.engine = PdfEngine()
        self.translator = Translator()
        self.document = None

        self.setWindowTitle("PDF Translator")
        self.resize(1100, 800)
        self.showMaximized()

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # ---------- Верхняя панель ----------

        row = QHBoxLayout()

        row.addWidget(QLabel("PDF"))

        self.edFile = QLineEdit()
        self.edFile.setReadOnly(True)
        row.addWidget(self.edFile)

        self.btnOpen = QPushButton("Выбрать PDF")
        self.btnOpen.clicked.connect(self.open_pdf)
        row.addWidget(self.btnOpen)

        layout.addLayout(row)

        # ---------- Панель управления ----------

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

        row2.addSpacing(20)

        row2.addWidget(QLabel("Блок"))

        self.spinBlock = QSpinBox()
        self.spinBlock.setMinimum(1)
        self.spinBlock.setMaximum(1)
        self.spinBlock.setEnabled(False)
        self.spinBlock.valueChanged.connect(self.show_page)
        row2.addWidget(self.spinBlock)

        self.btnBlockInfo = QPushButton("Свойства блока")
        self.btnTranslate = QPushButton("Перевести блок")
        self.btnTranslate.setEnabled(False)
        self.btnTranslate.clicked.connect(self.translate_block)
        row2.addWidget(self.btnTranslate)
        self.btnBlockInfo.setEnabled(False)
        self.btnBlockInfo.clicked.connect(self.inspect_selected_block)
        row2.addWidget(self.btnBlockInfo)

        row2.addStretch()

        layout.addLayout(row2)

                # ---------- Нижняя часть окна ----------

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # ---------- Левая панель ----------

        left = QWidget()
        leftLayout = QVBoxLayout(left)

        leftLayout.addWidget(QLabel("Информация"))

        self.info = QTextEdit()
        self.info.setMaximumHeight(180)
        self.info.setReadOnly(True)
        leftLayout.addWidget(self.info)

        leftLayout.addWidget(QLabel("Блоки"))

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        leftLayout.addWidget(self.text)
        leftLayout.addWidget(QLabel("Перевод"))

        self.translation = QTextEdit()
        self.translation.setReadOnly(True)
        leftLayout.addWidget(self.translation)

        splitter.addWidget(left)

        # ---------- Правая панель ----------

        right = QWidget()
        rightLayout = QVBoxLayout(right)

        rightLayout.addWidget(QLabel("Страница"))

        self.pageView = QLabel()

        self.pageView.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored
        )

        self.pageView.setStyleSheet(
            "border: 1px solid gray; background: white;"
        )

        rightLayout.addWidget(self.pageView)

        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #808080;
            }
        """)

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
        self.spinBlock.setEnabled(True)
        self.btnBlockInfo.setEnabled(True)
        self.btnTranslate.setEnabled(True)
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
        self.show_page()
        self.current_page = page
        self.spinBlock.setMaximum(max(1, len(page.blocks)))
        self.spinBlock.setValue(1)

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

    def inspect_selected_block(self):

        if not hasattr(self, "current_page"):
            return

        if not self.current_page.blocks:
            return

        index = self.spinBlock.value() - 1

        if index < 0 or index >= len(self.current_page.blocks):
            return

        self.info.clear()
        block = self.current_page.blocks[index]

        self.info.append("")
        self.info.append(f"=== Свойства блока №{self.spinBlock.value()} ===")
        self.info.append(f"Блок №{self.spinBlock.value()}")
        self.info.append(f"BBox : {block.bbox}")
        self.info.append("")
        self.info.append(f"Строк в блоке : {len(block.lines)}")
        self.info.append("")

        for line_no, line in enumerate(block.lines, start=1):

            self.info.append(f"===== Строка {line_no} =====")
            self.info.append(f"BBox : {line.bbox}")
            self.info.append(f"Span : {len(line.spans)}")
            self.info.append("")

            for span_no, span in enumerate(line.spans, start=1):

                self.info.append(f"  ----- Span {span_no} -----")
                self.info.append(f"  Font     : {span.font}")
                self.info.append(f"  Size     : {span.size}")
                self.info.append(f"  Flags    : {span.flags}")
                self.info.append(f"  Color    : {getattr(span, 'color', 'НЕТ')}")
                self.info.append(f"  Origin   : {getattr(span, 'origin', 'НЕТ')}")
                self.info.append(f"  Asc      : {getattr(span, 'ascender', 'НЕТ')}")
                self.info.append(f"  Desc     : {getattr(span, 'descender', 'НЕТ')}")
                self.info.append(f"  BBox     : {getattr(span, 'bbox', 'НЕТ')}")
                self.info.append(f"  Text     : {span.text}")
                self.info.append("")

    def show_page(self):

        if self.document is None:
            return

        selected = -1

        if hasattr(self, "current_page"):
            selected = self.spinBlock.value() - 1

        image = self.engine.render_page(
            self.document.filename,
            self.spin.value(),
            selected
        )

        pixmap = QPixmap.fromImage(image)

        self.pageView.setPixmap(
            pixmap.scaled(
                self.pageView.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def page_clicked(self, x, y):

        if self.document is None:
            return

        if not hasattr(self, "current_page"):
            return

        #
        # Координаты сцены -> координаты PDF
        #

        zoom = 1.5

        pdf_x = x / zoom
        pdf_y = y / zoom

        block_no = self.engine.find_block(
            self.document.filename,
            self.spin.value(),
            pdf_x,
            pdf_y
        )

        print(
            f"Scene: ({x:.1f}, {y:.1f})   "
            f"PDF: ({pdf_x:.1f}, {pdf_y:.1f})   "
            f"Block: {block_no}"
        )

        if block_no >= 0:

            self.spinBlock.setValue(block_no + 1)
            self.inspect_selected_block()   

    def translate_block(self):

        if not hasattr(self, "current_page"):
            return

        if not self.current_page.blocks:
            return

        index = self.spinBlock.value() - 1

        if index < 0 or index >= len(self.current_page.blocks):
            return

        block = self.current_page.blocks[index]

        self.translation.clear()
        self.translation.append("Оригинал")
        self.translation.append("")
        self.translation.append(block.text)
        self.translation.append("")
        self.translation.append("-" * 60)
        self.translation.append("")
        self.translation.append("Перевод")
        self.translation.append("")

        try:
            translated = self.translator.translate(block.text)
            self.translation.append(translated)

        except Exception as e:
            self.translation.append(f"Ошибка перевода:\n{e}")                        