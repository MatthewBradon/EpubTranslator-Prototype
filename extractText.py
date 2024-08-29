import ebooklib 
from ebooklib import epub
from bs4 import BeautifulSoup


def epub2thtml(epub_path):    
    book = epub.read_epub(epub_path)    
    chapters = []    
    for item in book.get_items():        
        if item.get_type() == ebooklib.ITEM_DOCUMENT:            
            chapters.append(item.get_content())    
    return chapters


# Example usage
# filePath = "rawEpub/Ascendance of a Bookworm Part 5 volume 8.epub"
filePath = "rawEpub/この素晴らしい世界に祝福を！ 01　あぁ、駄女神さま.epub"
chapters = epub2thtml(filePath)
print(len(chapters))

