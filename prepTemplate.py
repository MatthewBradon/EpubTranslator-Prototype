import zipfile
import os
import shutil

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

# Create a new EPUB file
with zipfile.ZipFile('output.epub', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk('export/output'):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, 'export/output')
            zf.write(full_path, relative_path)

# # Clean up
# shutil.rmtree('export/output')
# shutil.rmtree('unzipped/')
