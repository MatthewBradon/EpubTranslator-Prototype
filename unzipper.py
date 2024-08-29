import zipfile
import os

def extract_epub(epub_file, output_dir):
    # Unzip and save the contents of the epub file
    with zipfile.ZipFile(epub_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    


# Example usage
# title = 'この素晴らしい世界に祝福を！ 01　あぁ、駄女神さま.epub'
title = 'template.epub'
epub_file = 'rawEpub/' + title
output_dir = 'unzipped/' + title
extract_epub(epub_file, output_dir)