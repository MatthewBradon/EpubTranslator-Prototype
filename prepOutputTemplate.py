import zipfile
import os
import shutil
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


filePath = 'rawEpub/template.epub'
EpubToConvert = 'rawEpub/この素晴らしい世界に祝福を！ 01　あぁ、駄女神さま.epub'

EpubChapterList = []

# Unzip template into /export
with zipfile.ZipFile(filePath, 'r') as zip_ref:
    zip_ref.extractall('export/output')

# Unzip epub to convert into /unzipped
with zipfile.ZipFile(EpubToConvert, 'r') as zip_ref:
    zip_ref.extractall('unzipped/')


# Get a list of all the xhtml files in the EpubToConvert
for root, dirs, files in os.walk('unzipped/'):
    for file in files:
        if file.endswith('.xhtml'):
            EpubChapterList.append(file)


# print(EpubChapterList)

# Duplicate Section0001.xhtml for each chapter in EpubToConvert
for chapter in EpubChapterList:
    shutil.copy('export/output/OEBPS/Text/Section0001.xhtml', 'export/output/OEBPS/Text/' + chapter)


# Add the new chapters to the spine
spine = []

with open('export/output/OEBPS/content.opf', 'r') as file:
    data = file.readlines()
    for line in data:
        if '<spine>' in line:
            spine.append(line)
            for chapter in EpubChapterList:
                spine.append('    <itemref idref="' + chapter + '" />\n')
        else:
            spine.append(line)


with open('export/output/OEBPS/content.opf', 'w') as file:
    file.writelines(spine)


# Add the new chapters to the manifest
manifest = []

with open('export/output/OEBPS/content.opf', 'r') as file:
    data = file.readlines()
    for line in data:
        if '<manifest>' in line:
            for chapter in EpubChapterList:
                manifest.append('    <item id="' + chapter + '" href="Text/' + chapter + '" media-type="application/xhtml+xml" />\n')
        else:
            manifest.append(line)


with open('export/output/OEBPS/content.opf', 'w') as file:
    file.writelines(manifest)



# Remove Section0001.xhtml from the spine
spine = []

with open('export/output/OEBPS/content.opf', 'r') as file:
    data = file.readlines()
    for line in data:
        if '<itemref idref="Section0001.xhtml"/>' in line:
            continue
        else:
            spine.append(line)


with open('export/output/OEBPS/content.opf', 'w') as file:
    file.writelines(spine)



# Remove Section0001.xhtml from the manifest
manifest = []

with open('export/output/OEBPS/content.opf', 'r') as file:
    data = file.readlines()
    for line in data:
        if '<item id="Section0001.xhtml" href="Text/Section0001.xhtml" media-type="application/xhtml+xml"/>' in line:
            continue
        else:
            manifest.append(line)


with open('export/output/OEBPS/content.opf', 'w') as file:
    file.writelines(manifest)


# Remove Section0001.xhtml from the Text folder
os.remove('export/output/OEBPS/Text/Section0001.xhtml')


# Remove Section0001.xhtml from the nav.xhtml 
with open('export/output/OEBPS/Text/nav.xhtml', 'r') as file:
    data = file.readlines()

with open('export/output/OEBPS/Text/nav.xhtml', 'w') as file:
    for line in data:
        if '<a href="Section0001.xhtml">Section0001.xhtml</a>' in line:
            continue
        
        else:
            file.write(line)


# Add the new chapters to the nav.xhtml
with open('export/output/OEBPS/Text/nav.xhtml', 'r') as file:
    data = file.readlines()

inNav = False
with open('export/output/OEBPS/Text/nav.xhtml', 'w') as file:
    for line in data:
        file.write(line)
        if '<nav epub:type="toc" id="toc" role="doc-toc">'  in line:
            inNav = True
        if '<ol>' in line and inNav == True:
            for chapter in EpubChapterList:
                file.write('        <li><a href="'+chapter+'">'+chapter+'</a></li> \n')
            inNav = False
    

# Make into Epub
shutil.make_archive('output', 'zip', 'export/output')

os.rename('output.zip', 'output.epub')
