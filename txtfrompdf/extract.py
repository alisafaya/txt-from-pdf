# -*- coding: utf-8 -*-

import logging
import os
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from io import BytesIO
from typing import Union

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from .filter import post_process
from .fix_unicode import handle_custom_fonts
from .utils import temp_directory


logger = logging.getLogger(__name__)


def get_size_per_page(path):
    try:
        num_pages = len(PdfReader(path).pages)
        file_size = os.path.getsize(path)
        return file_size / num_pages
    except PdfReadError as e:
        logger.error(f"Read failed for path {path}")

        raise e


def process_pages(pdf_path: str, page_nums: int, output_dir: str):
    try:
        with open(pdf_path, "rb") as file:
            pdf_obj = PdfReader(file)
            for page_num in page_nums:
                output_fname = os.path.join(output_dir, f"{page_num + 1}.pdf")
                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_obj.pages[page_num])
                with open(output_fname, "wb") as out:
                    pdf_writer.write(out)
    except PdfReadError as e:
        logger.error(f"Read failed for pages {page_nums}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error for pages {page_nums}: {str(e)}")
        raise e


def split_pdf(pdf_path: str, output_dir: str):
    with open(pdf_path, "rb") as file:
        pdf_obj = PdfReader(file)
        num_pages = len(pdf_obj.pages)

        if num_pages == 1:
            return [pdf_path]

    # Create chunks of page numbers
    max_workers = os.cpu_count() or 1
    chunk_size = min(max(num_pages // max_workers, 1), 32)
    page_chunks = [
        range(i, min(i + chunk_size, num_pages))
        for i in range(0, num_pages, chunk_size)
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_pages, pdf_path, chunk, output_dir): chunk
            for chunk in page_chunks
        }

        for future in as_completed(futures):
            chunk = futures[future]
            try:
                _ = future.result()
            except Exception as exc:
                logger.error(
                    f"Generated an exception: {exc} for pages {chunk} of {pdf_path} during splitting"
                )
                raise exc

    return [
        os.path.join(output_dir, f"{page_num + 1}.pdf") for page_num in range(num_pages)
    ]


def pdf_to_text(path: Union[str, BytesIO]) -> str:
    retstr = BytesIO()
    manager = PDFResourceManager()
    layout = LAParams(all_texts=True, detect_vertical=True)
    device = TextConverter(manager, retstr, laparams=layout)
    interpreter = PDFPageInterpreter(manager, device)

    try:
        filepath = open(path, "rb") if isinstance(path, str) else path
        for page in PDFPage.get_pages(filepath, check_extractable=False):
            interpreter.process_page(page)

    except (PDFSyntaxError, TypeError):
        logger.error("ERROR: Extraction failed.")

    text = retstr.getvalue()
    device.close()
    retstr.close()

    if isinstance(path, str):
        filepath.close()

    try:
        text = handle_custom_fonts(text, path)
    except Exception:
        logger.warning(f"Failed to handle custom fonts for {path}")

    return text.decode("utf-8")  # decode from bytes to text


def _extract_txt_from_pdf(pdf_file, split_into_pages=True, process_output=True):
    if not split_into_pages:
        text = pdf_to_text(pdf_file)
    else:
        with temp_directory() as temp_dir:
            # Save bytes to a temporary file
            if isinstance(pdf_file, BytesIO):
                pdf_file_path = os.path.join(temp_dir, "temp.pdf")
                with open(pdf_file_path, "wb") as f:
                    f.write(pdf_file.getvalue())
            else:
                pdf_file_path = pdf_file

            # Split PDF into individual pages
            pages = split_pdf(pdf_file_path, temp_dir)

            if len(pages) == 1:
                text = pdf_to_text(pages[0])
            else:
                # Extract text from each page in parallel
                with ProcessPoolExecutor() as executor:
                    futures = {executor.submit(pdf_to_text, page): page for page in pages}
                    texts = {}

                    for future in as_completed(futures):
                        page = futures[future]
                        try:
                            texts[page] = future.result()
                        except Exception as exc:
                            logger.error(f"Generated an exception: {exc} for page {page}")
                            raise exc

                # Combine text from all pages
                text = ""
                for page in pages:
                    text += texts[page]

    # Post-process text
    if process_output:
        text = post_process(text, pdf_file)

    return text


def extract_txt_from_pdf(
    pdf_file: Union[str, BytesIO],
    split_into_pages: bool = True,
    process_output: bool = True,
):
    """
    Extracts text from a PDF file and saves it to a text file.

    Args:
        pdf_file (Union[str, BytesIO]): Path to the PDF file or a BytesIO object.
        split_into_pages (bool, optional): Whether to split the PDF into individual pages during extraction or not. Defaults to False.
        process_output (bool, optional): Whether to post-process the extracted text. Defaults to True.

    Returns:
        str: Extracted text from the PDF file.
    """
    if isinstance(pdf_file, bytes):
        # Convert bytes to BytesIO object
        pdf_file = BytesIO(pdf_file)

    try:
        text = _extract_txt_from_pdf(
            pdf_file, split_into_pages=split_into_pages, process_output=process_output
        )
        return text
    except PdfReadError:
        split_into_pages = not split_into_pages
        logger.error(
            f"PDF Extraction failed! Retrying with split_into_pages={split_into_pages}"
        )
        try:
            text = _extract_txt_from_pdf(
                pdf_file,
                split_into_pages=split_into_pages,
                process_output=process_output,
            )
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_file}")
            traceback.print_exc()
            raise e
