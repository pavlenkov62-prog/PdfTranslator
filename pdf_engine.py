from pathlib import Path
import fitz

from models import PdfDocument, PageInfo, TextBlock, TextLine, TextSpan


class PdfEngine:

    def load(self, filename: str) -> PdfDocument:
        src = fitz.open(filename)

        document = PdfDocument()
        document.filename = str(Path(filename))
        document.page_count = src.page_count
        document.file_size = Path(filename).stat().st_size
        document.toc = src.get_toc()
        document.has_toc = len(document.toc) > 0

        for page_index in range(src.page_count):
            page = src.load_page(page_index)

            page_info = PageInfo(
                number=page_index + 1,
                width=page.rect.width,
                height=page.rect.height,
                rotation=page.rotation,
            )

            if page.get_links():
                document.has_links = True

            data = page.get_text("dict")

            block_no = 0

            for block in data["blocks"]:
                if "lines" not in block:
                    continue

                text_block = TextBlock(
                    page=page_index + 1,
                    number=block_no,
                    bbox=tuple(block["bbox"]),
                )
                block_no += 1

                for line in block["lines"]:
                    text_line = TextLine(bbox=tuple(line["bbox"]))

                    for span in line["spans"]:
                        text_line.spans.append(
                             TextSpan(
                                text=span.get("text", ""),
                                font=span.get("font", ""),
                                size=span.get("size", 0.0),
                                color=span.get("color", 0),
                                flags=span.get("flags", 0),
                                bbox=tuple(span.get("bbox", (0, 0, 0, 0))),
                                origin=tuple(span.get("origin", (0, 0))),
                                ascender=span.get("ascender", 0.0),
                                descender=span.get("descender", 0.0),
                            )
                        )

                    if text_line.text.strip():
                        text_block.lines.append(text_line)

                if text_block.text.strip():
                    page_info.blocks.append(text_block)

            document.pages.append(page_info)

        src.close()
        return document
