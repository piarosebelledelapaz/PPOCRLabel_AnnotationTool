import fitz
import os
import argparse


# Function to clean file names
def clean_file_name(file_name):
    umlaut_map = {
        'ä': 'a', 'ö': 'o', 'ü': 'u', 'Ä': 'A', 'Ö': 'O', 'Ü': 'U', 'ß': 'ss'
    }

    cleaned_name = file_name.strip().replace(" ", "_")

    for umlaut, replacement in umlaut_map.items():
        cleaned_name = cleaned_name.replace(umlaut, replacement)
    return cleaned_name


def convert_pdfs(input_dir, output_dir):
    dpi = 300
    zoom = dpi / 72
    magnify = fitz.Matrix(zoom, zoom)

    os.makedirs(output_dir, exist_ok=True)

    for pdf_file in os.listdir(input_dir):
        if pdf_file.endswith(".pdf"):
            cleaned_file_name = clean_file_name(pdf_file)
            if cleaned_file_name != pdf_file:
                original_path = os.path.join(input_dir, pdf_file)
                new_path = os.path.join(input_dir, cleaned_file_name)
                os.rename(original_path, new_path)
                pdf_file = cleaned_file_name

            pdf_path = os.path.join(input_dir, pdf_file)
            pdf_doc = fitz.open(pdf_path)

            for page_number, page in enumerate(pdf_doc.pages(), start=1):
                pix = page.get_pixmap(matrix=magnify)

                output_file_name = f"{os.path.splitext(pdf_file)[0]}_page_{page_number}.jpeg"
                output_path = os.path.join(output_dir, output_file_name)
                pix.save(output_path)

            pdf_doc.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF files to images.")
    parser.add_argument("input_dir", type=str, help="Path to the directory containing PDF files.")
    parser.add_argument("output_dir", type=str, help="Path to the directory to save converted images.")
    args = parser.parse_args()

    convert_pdfs(args.input_dir, args.output_dir)
