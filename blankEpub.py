import zipfile
from io import BytesIO

def create_blank_epub(epub_file):
    # Create a ZIP archive for the EPUB file
    epub_zip = zipfile.ZipFile(BytesIO(), 'w')

    # Add a single blank XHTML file to the EPUB archive
    xhtml_file_name = 'content.xhtml'
    xhtml_file_data = b''
    epub_zip.writestr(xhtml_file_name, xhtml_file_data)

    # Close the ZIP archive
    epub_zip.close()

    # Save the ZIP archive to a file
    with open(epub_file, 'wb') as f:
        f.write(epub_zip.getvalue())

# Create and save the blank EPUB file
epub_file = 'blank_epub.epub'
create_blank_epub(epub_file)