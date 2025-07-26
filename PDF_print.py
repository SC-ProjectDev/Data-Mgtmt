import pdfplumber
import os

def print_pdf_contents_with_line_numbers(pdf_path):
    """Extract and print all text from each page of the PDF with line numbers."""
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            print("PDF has no pages.")
            return

        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            print(f"--- Page {page_num} ---")
            if text:
                # Split the text into lines and print each with its line number.
                lines = text.splitlines()
                for line_index, line in enumerate(lines, start=1):
                    print(f"[Line {line_index}] {line}")
            else:
                print("No text found on this page.")
            print("-" * 40)

def main():
    pdf_path = input("Enter the full path to your PDF file: ").strip()
    print_pdf_contents_with_line_numbers(pdf_path)

if __name__ == "__main__":
    main()
