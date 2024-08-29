import zipfile
import os
import shutil
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

filePath = "rawEpub/Ascendance of a Bookworm Part 5 volume 8.epub"
# Create copy of epub file
shutil.copy(filePath, 'templateEpub/EpubToConvert')

# Rename copy of epub file
os.rename('templateEpub/Ascendance of a Bookworm Part 5 volume 8.epub', 'templateEpub/template.epub')


def epub2thtml(epub_path):    
    book = epub.read_epub(epub_path)    
    chapters = []    
    for item in book.get_items():        
        if item.get_type() == ebooklib.ITEM_DOCUMENT:            
            chapters.append(item.get_content())    
    return chapters

chapters = epub2thtml('templateEpub/template.epub')


# Unzip and save the contents of the epub file
with zipfile.ZipFile('templateEpub/template.epub', 'r') as zip_ref:
    zip_ref.extractall('templateEpub/unzipped/')