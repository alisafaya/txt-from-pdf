def cli_main():
    import argparse
    import glob
    import logging
    import os

    from .extract import extract_txt_from_pdf

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(
        description="txt-from-pdf CLI - Extracts cleaned text from PDF files"
    )
    parser.add_argument(
        "--input",
        help="Path to a folder containing PDFs or to a single PDF file. (Required)",
        required=True,
    )
    parser.add_argument(
        "--output",
        help="Output location for the extracted text files. (Optional, default: 'extracted_text')",
        required=False,
        default="extracted_text",
    )
    parser.add_argument(
        "--no_filter",
        help="Turn off cleaning and filtering of the resulting text files. (Optional)",
        action="store_true",
    )

    args = parser.parse_args()

    if os.path.isfile(args.input):
        all_pdfs = [args.input]
    elif os.path.isdir(args.input):
        all_pdfs = sorted(glob.glob(f"{args.input}/**/*.pdf", recursive=True))
    else:
        raise ValueError("Invalid input path")

    logger.info("Starting extraction with txt-from-pdf")
    logger.info(f"Input path: {args.input}")
    logger.info(f"Found {len(all_pdfs)} PDF files")

    try:
        os.makedirs(args.output, exist_ok=True)
    except FileExistsError:
        logger.warning("Output directory already exists")

    for pdf in all_pdfs:
        logger.info(f"Extracting: {pdf}")
        text = extract_txt_from_pdf(pdf, process_output=not args.no_filter)
        output_file = os.path.join(
            args.output, f"{os.path.basename(pdf).replace('.pdf', '.txt')}"
        )

        with open(output_file, "w") as f:
            f.write(text)
        logger.info(f"Saved to: {output_file}")
