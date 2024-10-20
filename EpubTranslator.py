import zipfile
import os
import shutil
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from transformers import AutoTokenizer
import torch
import sys
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from onnxruntime import InferenceSession, SessionOptions, get_available_providers
from onnxManual import runTranslation

def run(epubPath, finalZipPath):

    # Path to the directory containing the ONNX models and config files
    model_path = 'onnx-model-dir'

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en')
    # model = ORTModelForSeq2SeqLM.from_pretrained(model_path)

    encoder_path = 'onnx-model-dir/encoder_model.onnx'
    decoder_path = 'onnx-model-dir/decoder_model.onnx'

    encoder_session = InferenceSession(encoder_path)
    decoder_session = InferenceSession(decoder_path)


    filePath = 'rawEpub/template.epub'


    EpubToConvert = epubPath


    # EpubToConvert = 'rawEpub\Ascendance of a Bookworm Part 5 volume 11 『Premium Ver』.epub'
    xhtmlFiles = []
    EpubChapterList = []



    # Unzip template into /export
    with zipfile.ZipFile(filePath, 'r') as zip_ref:
        zip_ref.extractall('export/output')

    # Unzip epub to convert into /unzipped
    with zipfile.ZipFile(EpubToConvert, 'r') as zip_ref:
        zip_ref.extractall('unzipped/')


    book = epub.read_epub(EpubToConvert)
    spine_order_ids = [item_id for item_id, _ in book.spine]


    # Get a list of all the xhtml files in the EpubToConvert
    for root, dirs, files in os.walk('unzipped/'):
        for file in files:
            if file.endswith('.xhtml'):
                EpubChapterList.append(file)
                xhtmlFiles.append(os.path.join(root, file))

    EpubChapterList = spine_order_ids


    # Check if spine_order_ids has xhtml extension if not add it
    for index, chapter in enumerate(EpubChapterList):
        if not chapter.endswith('.xhtml'):
            EpubChapterList[index] = f'{chapter}.xhtml'


    # Duplicate Section0001.xhtml for each chapter in EpubToConvert
    for chapter in EpubChapterList:
        shutil.copy('export/output/OEBPS/Text/Section0001.xhtml', f'export/output/OEBPS/Text/{chapter}')





    # Update the content.opf file
    with open('export/output/OEBPS/content.opf', 'r') as file:
        data = file.readlines()

    manifest = []
    spine = []
    inside_manifest = False
    inside_spine = False

    for line in data:
        if '<manifest>' in line:
            manifest.append(line)
            inside_manifest = True
        elif '</manifest>' in line:
            inside_manifest = False
            for index, chapter in enumerate(EpubChapterList, start=1):
                chapter_id = f'chapter{index}'
                manifest.append(f'    <item id="{chapter_id}" href="Text/{chapter}" media-type="application/xhtml+xml"/>\n')
            manifest.append(line)
        elif '<spine>' in line:
            spine.append(line)
            inside_spine = True
        elif '</spine>' in line:
            inside_spine = False
            for index, chapter in enumerate(EpubChapterList, start=1):
                chapter_id = f'chapter{index}'
                spine.append(f'    <itemref idref="{chapter_id}" />\n')
            spine.append(line)
        elif inside_manifest:
            if 'Section0001.xhtml' not in line:  # Remove Section0001.xhtml from manifest
                manifest.append(line)
        elif inside_spine:
            if 'Section0001.xhtml' not in line:  # Remove Section0001.xhtml from spine
                spine.append(line)
        else:
            manifest.append(line)

    # Now combine the manifest and spine sections correctly
    final_output = manifest[:-1] + spine + [manifest[-1]]

    # Write the updated manifest and spine back into content.opf
    with open('export/output/OEBPS/content.opf', 'w') as file:
        file.writelines(final_output)




    # Remove Section0001.xhtml from the Text folder
    os.remove('export/output/OEBPS/Text/Section0001.xhtml')






    # Update nav.xhtml to remove Section0001.xhtml entry and reflect new chapters
    with open('export/output/OEBPS/Text/nav.xhtml', 'r') as file:
        data = file.readlines()

    nav = []
    inside_nav = False

    for line in data:
        nav.append(line)
        if '<nav epub:type="toc" id="toc" role="doc-toc">' in line:
            inside_nav = True
        if '<ol>' in line and inside_nav:
            for index, chapter in enumerate(EpubChapterList, start=1):
                chapter_filename = os.path.basename(chapter)
                nav.append(f'        <li><a href="{chapter_filename}">Chapter {index}</a></li>\n')
            inside_nav = False

    # Write the updated nav.xhtml file
    with open('export/output/OEBPS/Text/nav.xhtml', 'w') as file:
        file.writelines(nav)





    #Copy all the images from the unzipped epub to the output epub
    os.makedirs("export/output/OEBPS/Images/", exist_ok=True)
    for root, dirs, files in os.walk('unzipped/'):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                shutil.copy(os.path.join(root, file), f'export/output/OEBPS/Images/{file}')







    # Add all p tags and img tags to the respective chapter in the output epub
    for chapter in xhtmlFiles:
        with open(chapter, 'r', encoding='utf-8') as file:
            data = file.read()

        soup = BeautifulSoup(data, 'html.parser')

        # Extract the body content
        body = soup.body

        chapter_content = []

        # Loop through all elements in the body
        for element in body.descendants:
            # Handle p tags and extract their text
            if element.name == 'p':
                # Extract all text within the <p> tag, ignoring inner tags
                p_text = element.get_text(strip=True)
                #Check if the text is empty
                if not p_text:
                    continue
                
                # Translate the text to English
                # inputs = tokenizer(p_text, return_tensors='pt')
                # translated = model.generate(inputs['input_ids'])
                # english_text = tokenizer.decode(translated[0], skip_special_tokens=True)
                english_text = runTranslation(p_text, tokenizer, encoder_session, decoder_session)
                print(english_text)
                chapter_content.append(f'<p>{english_text}</p>\n')

            # Handle img tags and reformat them
            elif element.name == 'img':
                img_src = element['src']
                img_filename = os.path.basename(img_src)
                chapter_content.append(f'<img src="../Images/{img_filename}"/>\n')
        print("Chapter done")
        # If the body is empty, preserve other content
        chapter_content_str = "".join(chapter_content) if chapter_content else str(body)

        # Construct the XHTML content
        xhtml_content = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
            '<head>\n'
            f'  <title>{os.path.basename(chapter)}</title>\n'
            '</head>\n'
            '<body>\n'
            f'{chapter_content_str}\n'
            '</body>\n'
            '</html>'
        )

        # Write the processed content to a new file
        output_path = f'export/output/OEBPS/Text/{os.path.basename(chapter)}'
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(xhtml_content)




    # Create a new EPUB file
    with zipfile.ZipFile(os.path.join(finalZipPath, 'translatedEpub.epub'), 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk('export/output'):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, 'export/output')
                zf.write(full_path, relative_path)


    # Clean up the temporary directories
    # shutil.rmtree('export')
    # shutil.rmtree('unzipped')