import os
import requests
from PIL import Image
import pytesseract
from fpdf import FPDF
import openai

# Set up API key
openai.organization = "org-udXIP3LL8x0YUl1cNkdLubBg"
openai.api_key = "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"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract text from an image
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='deu+eng')
    return text

# Function to make an API request to OpenAI
def make_gpt_request(prompt, max_tokens=256, model="text-davinci-003", temperature=1, text=""):
    endpoint = f"https://api.openai.com/v1/engines/{model}/completions"
    
    # Define parameters for API request
    params = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "context": text
    }

    # Make API request with authentication header
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    response = requests.post(endpoint, json=params, headers=headers)

    # Return response
    return response.json()["choices"][0]["text"]

# Create the PDF document
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# German Section
pdf.set_font('Arial', 'B', 16)
pdf.multi_cell(0, 10, 'German Section', align='L')
pdf.ln(10)
pdf.set_font('Arial', '', 12)

# English Section
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.multi_cell(0, 10, 'English Section', align='L')
pdf.ln(10)
pdf.set_font('Arial', '', 12)

# Specify the image directory path
image_dir = os.path.join(os.getcwd(), "image analyser project", "img")

# Traverse through the image directories, extract text, and process the information
for subdir, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith((".jpg", ".png", ".JPG")):
            image_path = os.path.join(subdir, file)
            extracted_text = extract_text_from_image(image_path)

            # Process the extracted text and extract required information using GPT-3
            prompt = f"Extract the article name (excluding bofrost), article number, MHD, (LAX or production code or batch or LOT) from:\n{extracted_text}\nUse the following format:\nArticle name: <ArticleName>; Article number: <ArticleNumber>; MHD: <MHD>; etc..."
            processed_text = make_gpt_request(prompt, model="text-davinci-003", max_tokens=256, temperature=1, text=extracted_text)

            # Add the extracted information to the PDF (German Section)
            pdf.cell(0, 10, f"Image: {file}", ln=True)
            pdf.multi_cell(0, 10, processed_text, ln=True)

            # Add the extracted information to the PDF (English Section)
            pdf.add_page()
            pdf.cell(0, 10, f"Image: {file}", ln=True)
            english_processed_text = make_gpt_request(prompt, model="text-davinci-003", max_tokens=256, temperature=1, text=extracted_text)
            pdf.multi_cell(0, 10, english_processed_text, ln=True)

            # Get current position for next image placement
            x = pdf.get_x()
            y = pdf.get_y()

            # Add the image to the PDF
            pdf.image(image_path, x=x + 10, y=y + 15, w=80)
            pdf.set_xy(x, y + 100)

            pdf.ln(10)

# Save the PDF document
pdf.output("image_information.pdf")
