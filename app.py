from flask import Flask, request, render_template, jsonify
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

def check_pdf_content_and_extract_text(pdf_path):
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        extracted_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()

            if text.strip():  # If text is found
                extracted_text += text  # Append extracted text from each page
            else:
                # Check for images if no text
                images = page.get_images(full=True)
                if images:
                    for img in images:
                        xref = img[0]  # Get the xref of the image
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Perform OCR on the image
                        ocr_text = pytesseract.image_to_string(image)
                        if ocr_text.strip():
                            return "Scanned Image with Text", ocr_text
                    return "Scanned Image without Text", None

        # Determine the PDF content type
        if extracted_text.strip():
            return "Text Document", extracted_text
        else:
            return "Unknown/Empty PDF", None

    except Exception as e:
        print(f"Error: {e}")
        return "Error reading the PDF", None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return jsonify({"error": "No file uploaded."}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({"error": "No file selected."}), 400
        
        file.save(file.filename)
        pdf_type, content = check_pdf_content_and_extract_text(file.filename)

        response = {
            "type": pdf_type,
            "content": content
        }
        return jsonify(response)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
