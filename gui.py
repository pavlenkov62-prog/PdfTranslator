from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
)

from pdf_engine import PdfInfo


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Translator")
        self.resize(900, 650)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        #
        # PDF
        #

        row = QHBoxLayout()

        layout.addLayout(row)

        row.addWidget(QLabel("PDF"))

        self.edFile = QLineEdit()

        self.edFile.setReadOnly(True)

        row.addWidget(self.edFile)

        self.btnOpen = QPushButton("Выбрать PDF")

        self.btnOpen.clicked.connect(self.open_pdf)

        row.addWidget(self.btnOpen)

        #
        # Translate
        #

        self.btnTranslate = QPushButton("Перевести")

        self.btnTranslate.setEnabled(False)

        layout.addWidget(self.btnTranslate)

        #
        # Log
        #

        layout.addWidget(QLabel("Информация"))

        self.log = QTextEdit()

        self.log.setReadOnly(True)

        layout.addWidget(self.log)

    # ---------------------------------------------------------

    def open_pdf(self):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            "Выберите PDF",

            "",

            "PDF (*.pdf)"

        )

        if not filename:
            return

        self.edFile.setText(filename)

        self.btnTranslate.setEnabled(True)

        pdf = PdfInfo(filename)

        self.log.clear()

        self.log.append("Документ")
        self.log.append("")
        self.log.append(pdf.filename.name)
        self.log.append("")
        self.log.append(f"Размер : {pdf.size_mb:.2f} МБ")
        self.log.append(f"Страниц : {pdf.page_count}")

        pdf.close()