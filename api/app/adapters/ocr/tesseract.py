from PIL import Image
import pytesseract

class TesseractOCR:
    def extract_text(self, image_path):
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
