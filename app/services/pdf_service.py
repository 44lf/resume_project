# services/pdf_service.py

import fitz  # PyMuPDF
import io


def parse_pdf(pdf_bytes: bytes):
    """
    返回：
    - text: 全文文本
    - images: [bytes, ...]
    """
    doc = fitz.open(stream=pdf_bytes,filetype='pdf')

    texts = []
    images = []

    for page in doc:
        # 文本
        texts.append(page.get_text())

        # 图片
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            images.append(base_image["image"])

    return "\n".join(texts), images
