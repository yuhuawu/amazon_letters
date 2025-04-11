import os
from pypdf import PdfReader, PdfWriter

def remove_1997_reprint(pdf_path, output_path):
    """
    Open a PDF, check its last page to see if it contains the string "1997"
    (indicating a reprinted 1997 letter) and, if so, remove that page.
    Writes a new PDF to output_path if removal happens.
    Returns the path to the sanitized PDF.
    """
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    index = -1
    # Extract text of last page – adjust the condition as necessary
    for i, page in enumerate(reader.pages[::-1]):
        text = page.extract_text() or ""
        if "Reprinted from the 1997 Annual Report" in text:
            print(f"Found '1997' in page: {num_pages - i} for file: {pdf_path}")
            index = num_pages - i
            break    
    else:
        print(f"No '1997' found in {pdf_path}, keeping all pages.")
        index = num_pages + 1
    writer = PdfWriter()
    for i in range(index - 1):
        print(f"Adding page {i} to new PDF")
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
    return output_path
    

def merge_pdfs_with_toc(pdf_list, output_pdf):
    """
    Merge PDFs provided as a list of (pdf_path, title) tuples.
    Creates bookmarks (table of contents) for each PDF.
    """
    writer = PdfWriter()
    current_page = 0  # track overall page count

    for pdf_path, title in pdf_list:
        reader = PdfReader(pdf_path)
        start_page = current_page
        for page in reader.pages:
            writer.add_page(page)
            current_page += 1
        # Add an outline item (bookmark) pointing to the start page for this PDF.
        writer.add_outline_item(title, start_page)
    
    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)
    print("Merged PDF created:", output_pdf)


def main():
    # Folder where your downloaded letter PDFs are located.
    download_folder = "downloads"
    # Folder for sanitized PDFs (with the last 1997 page removed).
    processed_folder = "processed"
    os.makedirs(processed_folder, exist_ok=True)
    
    pdf_list = []
    # Process all PDF files in the downloads folder.
    for file in sorted(os.listdir(download_folder)):
        if file.lower().endswith(".pdf"):
            pdf_in = os.path.join(download_folder, file)
            pdf_out = os.path.join(processed_folder, 'clean_'+file)
            sanitized_pdf = remove_1997_reprint(pdf_in, pdf_out)
            # Use the filename (without extension) as bookmark title.
            title = os.path.splitext(file)[0]
            pdf_list.append((sanitized_pdf, title))
            
    
    merged_pdf = "merged_letters.pdf"
    merge_pdfs_with_toc(pdf_list, merged_pdf)

if __name__ == "__main__":
    main()