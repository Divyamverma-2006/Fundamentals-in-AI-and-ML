# Fundamentals-in-AI-and-ML


````markdown
# ID Document Scanner & Extractor
### A simple, smart way to scan and extract details from Indian ID documents

This project is a Python-based tool that automatically detects what type of ID document you upload — like a PAN card, Aadhaar card, Driving License, or Board Certificate — and extracts important details using OCR.  
It supports both images and PDFs and uses Tesseract along with powerful image processing to improve accuracy.

---

## What This Tool Does

- **Detects the document type automatically**  
  No need to select anything — just upload your file.

- **Works with popular formats**  
  JPG, PNG, BMP, TIFF, and PDF.

- **Accurate text extraction**  
  Uses Tesseract OCR with multiple preprocessing steps to improve clarity.

- **Smart field extraction**  
  Pulls out names, dates, ID numbers, addresses, and more depending on the document type.

- **Image enhancement**  
  Cleans and sharpens the image so OCR gets better results.

---

## Supported Documents

| Document Type | Extracted Details |
|--------------|------------------|
| **PAN Card** | PAN Number, Name, Father’s Name, DOB |
| **Aadhaar Card** | Aadhaar Number, Name, DOB, Gender, Parent/Spouse Name, Full Address, Pincode |
| **Driving License** | License Number, Name, DOB, Issue Date, Validity, Blood Group |
| **Board Certificate** | Student Name, Roll No., DOB, Exam Year, Marks/Grades, Result |

---

## Requirements

### Python Packages
```bash
pip install opencv-python pytesseract Pillow numpy pdf2image
````

### Install Tesseract OCR

**Windows:**
Download from the official repo → install → add to PATH
Or set the path manually:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Mac:**

```bash
brew install tesseract
```

**Linux:**

```bash
sudo apt install tesseract-ocr
```

### Install Poppler (for PDF files)

**Windows:** Download & add the `bin` folder to PATH
**Mac:**

```bash
brew install poppler
```

**Linux:**

```bash
sudo apt-get install poppler-utils
```

---

## Installation

1. Clone or download this repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract
4. Install Poppler if you want PDF support

You’re ready to go!

---

## How to Use

Run the main script:

```bash
python document_scanner.py
```

Then enter the path to your file:

```
Enter the path to your document (image or PDF): C:/Documents/aadhaar.jpg
```

That’s it — the tool does the rest.

---

## Path Examples

**Windows:**

```
C:/Users/Name/Desktop/pan.jpg
```

**Mac/Linux:**

```
/home/user/docs/license.pdf
```

**Same folder as the script:**

```
aadhaar.png
```

---

## Sample Output

```
==================================================
ID Document Scanner (Images & PDFs)
==================================================

Enter the path to your document (image or PDF): aadhaar.jpg

File found! Processing...

==================================================
Document Type: Aadhaar Card

Extracted Details:
--------------------------------------------------
Aadhaar Number: 1234 5678 9012
Name: John Doe
Date of Birth: 15/08/1990
Gender: Male
Father/Husband Name: Richard Doe
Address: 123 Main Street, Mumbai
Pincode: 400001

==================================================
Processing Complete!
==================================================
```

---

## Tips for Better Results

* Use clear, high-resolution scans (300 DPI or more)
* Avoid tilted or angled photos
* Try to remove shadows or glare
* Prefer PDFs or clean PNG/JPEG images
* Remove plastic ID covers before scanning

Good inputs = accurate outputs ✔️

---

## Troubleshooting

### Tesseract isn’t working

* Make sure it’s installed
* Add it to your PATH
* Or manually set the command path

### PDF issues

* Install `pdf2image`
* Install Poppler
* Restart your terminal or IDE

### Poor extraction

* Try a clearer image
* Increase resolution
* Hold the camera steady

---

## Project Structure

```
project/
│── document_scanner.py
│── README.md
└── documents/
     ├── sample_pan.jpg
     ├── sample_aadhaar.pdf
     └── sample_license.png
```

---

## Behind the Scenes (How It Works)

### Image Processing Includes:

* Grayscale conversion
* Upscaling
* Sharpening & contrast improvement
* Noise removal
* Thresholding
* Morphological cleaning

### OCR Logic:

* Multiple Tesseract passes
* Regex-based extraction
* Date and address detection
* Smart filtering for names & numbers

---

## Limitations

* Struggles with low-quality photos
* Cannot read handwritten text
* Damaged or old documents may not OCR correctly
* Unusual document designs may fail detection

---

## Future Improvements

* Support for Passport, Voter ID, etc.
* OCR in Indian languages
* Batch processing mode
* GUI interface
* JSON/CSV export
* Document verification checks

---

## Contributions & Support

Issues, suggestions, and pull requests are always welcome.
If you’d like to contribute, feel free to jump in!

---

This project is open-source and free for personal and educational use.

```
