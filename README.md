
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
text = extract_txt_from_pdf(pdf_path)
print(text)
```

# CLI Usage

Single file:

```bash
txt-from-pdf --input file.pdf --output extracted-text 
```

Multiple files in a directory:

```bash
txt-from-pdf --input dir-with-pdfs --output extracted-text 
```

Detailed help:

```bash
usage: txt-from-pdf [-h] --input INPUT [--output OUTPUT] [--no_filter] [--size SIZE]

txt-from-pdf CLI - Extracts cleaned text from PDF files

options:
  -h, --help       show this help message and exit
  --input INPUT    Path to a folder containing PDFs or to a single PDF file. (Required)
  --output OUTPUT  Output location for the extracted text files. (Optional, default: 'extracted_text')
  --no_filter      Turn off cleaning the resulting text files. (Optional)
  --size SIZE      Maximum file size per page in bytes for processing (mostly images). (Optional, default: 300000)
```
