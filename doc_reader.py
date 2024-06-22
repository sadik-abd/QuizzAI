import pytesseract
from PIL import Image
from typing import List
import PyPDF2
from pdf2image import convert_from_path

def convert_to_strings(inputs) -> List[str]:
    outputs = []
    for inpt in inputs:
        text = pytesseract.image_to_string(inpt)
        outputs.append(text)

def load_pdf(path):
    texts = []
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Iterate over each page
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            texts.append(text)
    return texts

def load_pdf_ocr(path):
    if path.endswith("jpg") or path.endswith("png") or path.endswith("jpeg"):
        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        return [text]
    images = convert_from_path(path)
    texts = convert_to_strings(images)
    return texts
