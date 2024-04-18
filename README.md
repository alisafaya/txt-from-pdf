
# txt-from-pdf: Extract clean text from PDFs

[![Github release](https://img.shields.io/github/release/alisafaya/txt-from-pdf.svg)](https://github.com/alisafaya/txt-from-pdf/releases)
[![PyPI version](https://badge.fury.io/py/txt-from-pdf.svg)](https://badge.fury.io/py/txt-from-pdf)
[![GitHub license](https://img.shields.io/github/license/alisafaya/txt-from-pdf.svg)](./LICENSE)

Extracting text from pdfs using [pdfminer.six](https://github.com/pdfminer/pdfminer.six) and [pypdf](https://github.com/py-pdf/pypdf/). Adapted from [PDFextract](https://github.com/sdtblck/PDFextract).

# Installation

```bash
pip install txt-from-pdf
```

# Usage

```python
from txtfrompdf import extract_txt_from_pdf

pdf_path = "file.pdf"
text = extract_pdf(pdf_path)
print(text)
```
