# -*- coding: utf-8 -*-

import logging
import traceback
from io import BytesIO
from typing import Union

import pymupdf

from .filter import post_process


logger = logging.getLogger(__name__)


def pdf_to_text(path: Union[str, BytesIO]) -> str:
    if isinstance(path, BytesIO):
        document = pymupdf.open(stream=path)
    elif isinstance(path, str):
        document = pymupdf.open(filename=path)

    text = "\n\n\n".join(
        [
            "\n".join([block[4] for block in page.get_text("blocks")])
            for page in document
        ]
    )

    logger.debug(f"Extracted text from {path if isinstance(path, str) else 'BytesIO'}")
    return text


def _extract_txt_from_pdf(pdf_file, process_output=True):
    # Extract text from PDF using mupdf
    text = pdf_to_text(pdf_file)

    # Post-process text
    if process_output:
        logger.debug("Post-processing extracted text")
        text = post_process(text)

    return text


def extract_txt_from_pdf(pdf_file: Union[str, BytesIO], process_output: bool = True):
    """
    Extracts text from a PDF file and saves it to a text file.

    Args:
        pdf_file (Union[str, BytesIO]): Path to the PDF file or a BytesIO object.
        split_into_pages (bool, optional): Whether to split the PDF into individual
            pages during extraction or not. Defaults to False.
        process_output (bool, optional): Whether to post-process the extracted text.
            Defaults to True.

    Returns:
        str: Extracted text from the PDF file.
    """
    if isinstance(pdf_file, bytes):
        # Convert bytes to BytesIO object
        pdf_file = BytesIO(pdf_file)

    try:
        text = _extract_txt_from_pdf(pdf_file, process_output=process_output)
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_file}")
        traceback.print_exc()
        raise e
