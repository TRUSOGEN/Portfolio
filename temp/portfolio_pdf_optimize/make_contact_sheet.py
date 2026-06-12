"""渲染作品集 PDF 缩略图，便于人工检查分页和空白。

脚本读取最终导出的 PDF，将每页缩成网格图。它用于验证版面效果，不参与正式交付。
"""

from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image, ImageDraw


PDF_PATH = Path("/Users/trusoegn/resume/作品集/吴业亘_作品集.pdf")
OUT_PATH = Path("/Users/trusoegn/resume/portfolio/temp/portfolio_pdf_optimize/contact_sheet.jpg")
THUMB_WIDTH = 280
PADDING = 18
COLS = 4


def render_page(page: fitz.Page) -> Image.Image:
    """将单页 PDF 渲染为固定宽度缩略图。"""

    rect = page.rect
    scale = THUMB_WIDTH / rect.width
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def main() -> None:
    """生成包含全部页面的 contact sheet。"""

    doc = fitz.open(PDF_PATH)
    thumbs = [render_page(page) for page in doc]
    thumb_height = max(image.height for image in thumbs)
    rows = (len(thumbs) + COLS - 1) // COLS
    width = COLS * THUMB_WIDTH + (COLS + 1) * PADDING
    height = rows * (thumb_height + 26) + (rows + 1) * PADDING
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)

    for index, image in enumerate(thumbs):
        row, col = divmod(index, COLS)
        x = PADDING + col * (THUMB_WIDTH + PADDING)
        y = PADDING + row * (thumb_height + 26 + PADDING)
        sheet.paste(image, (x, y))
        draw.rectangle((x, y, x + image.width - 1, y + image.height - 1), outline=(190, 190, 190))
        draw.text((x, y + image.height + 6), f"Page {index + 1}", fill=(40, 40, 40))

    sheet.save(OUT_PATH, "JPEG", quality=88)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
