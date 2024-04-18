# -*- coding: utf-8 -*-

import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from .filter import post_process
from .utils import temp_directory


logger = logging.getLogger(__name__)

def get_size_per_page(path):
    try:
        num_pages = len(PdfReader(path).pages)
        file_size = os.path.getsize(path)
        return file_size / num_pages
    except PdfReadError as e:
        logger.error(f"Read failed for path {path}")
        traceback.print_exc()
        raise e


def copy_page(pdf_obj, page_num, output_fname):
    try:
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf_obj.pages[page_num])
        with open(output_fname, "wb") as out:
            pdf_writer.write(out)
    except PdfReadError as e:
        logger.error(f"Read failed for page {page_num}")
        traceback.print_exc()
        raise e


def split_pdf(pdf, output_dir):
    pdf_obj = PdfReader(pdf)
    pages = [
        os.path.join(output_dir, f"{page_num + 1}.pdf")
        for page_num in range(len(pdf_obj.pages))
    ]

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(copy_page, pdf_obj, page_num, page_path): page_num
            for page_num, page_path in zip(range(len(pdf_obj.pages)), pages)
        }

        for future in as_completed(futures):
            page_num = futures[future]
            try:
                _ = future.result()
            except Exception as exc:
                logger.error(
                    f"Generated an exception: {exc} for page {page_num} of {pdf} during splitting"
                )
                traceback.print_exc()
                raise exc

    return pages


def pdf_to_text(path):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = TextConverter(manager, retstr, laparams=layout)
    filepath = open(path, "rb")
    interpreter = PDFPageInterpreter(manager, device)

    try:
        for page in PDFPage.get_pages(filepath, check_extractable=True):
            interpreter.process_page(page)

    except (PDFSyntaxError, TypeError):
        logger.error(f"ERROR: Extraction failed for {path}")
        traceback.print_exc()

    text = retstr.getvalue()
    filepath.close()
    device.close()
    retstr.close()
    return text.decode("utf-8")  # decode from bytes to text




def extract_txt_from_pdf(pdf_file, split_into_pages=True, process_output=True):
    """
    Extracts text from a PDF file and saves it to a text file.

    Args:
        pdf_file (str): Path to the PDF file.
        split_into_pages (bool, optional): Whether to split the PDF into individual pages during extraction or not. Defaults to True.
        process_output (bool, optional): Whether to post-process the extracted text. Defaults to True.

    Returns:
        str: Extracted text from the PDF file.
    """
    if not split_into_pages:
        text = pdf_to_text(pdf_file)
    else:
        with temp_directory() as temp_dir:
            # Split PDF into individual pages
            pages = split_pdf(pdf_file, temp_dir)

            # Extract text from each page in parallel
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(pdf_to_text, page): page for page in pages
                }

                texts = {}
                for future in as_completed(futures):
                    page = futures[future]
                    try:
                        texts[page] = future.result()
                    except Exception as exc:
                        logger.error(f"Generated an exception: {exc} for page {page}")
                        traceback.print_exc()
                        raise exc

            # Combine text from all pages
            text = ""
            for page in pages:
                text += texts[page]

    # Post-process text
    if process_output:
        text = post_process(text, pdf_file)

    return text
