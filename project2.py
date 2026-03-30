import cv2
import pytesseract
import re
import os
import numpy as np
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class IDDocumentScanner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = None
        self.text = ""
        self.doc_type = None
        self.extracted_data = {}
        self.load_file()

    def load_file(self):
        file_ext = os.path.splitext(self.file_path)[1].lower()

        if file_ext == '.pdf':
            print("PDF detected. Converting to image...")
            try:
                images = convert_from_path(self.file_path, dpi=300, first_page=1, last_page=1)
                if images:
                    pil_image = images[0]
                    self.image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    print("PDF converted successfully!")
            except Exception as e:
                print(f"Error converting PDF: {e}")
        else:
            self.image = cv2.imread(self.file_path)

    def enhance_image(self, img):
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(2.0)

        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(2.0)

        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def preprocess_image_method1(self):
        enhanced = self.enhance_image(self.image)
        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        denoised = cv2.fastNlMeansDenoising(resized, None, 10, 7, 21)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def preprocess_image_method2(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LANCZOS4)
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return morph

    def extract_text(self):
        config1 = r'--oem 3 --psm 6 -l eng'
        config2 = r'--oem 3 --psm 3 -l eng'
        config3 = r'--oem 3 --psm 11 -l eng'

        img1 = self.preprocess_image_method1()
        img2 = self.preprocess_image_method2()

        text1 = pytesseract.image_to_string(img1, config=config1)
        text2 = pytesseract.image_to_string(img2, config=config2)
        text3 = pytesseract.image_to_string(img1, config=config3)

        self.text = text1 + "\n" + text2 + "\n" + text3

        return self.text

    def identify_document_type(self):
        text_lower = self.text.lower()

        if "income tax" in text_lower or "permanent account" in text_lower or re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
                                                                                        self.text):
            self.doc_type = "PAN Card"
        elif "aadhaar" in text_lower or "आधार" in self.text or "government of india" in text_lower or re.search(
                r'\b\d{4}\s?\d{4}\s?\d{4}\b', self.text):
            self.doc_type = "Aadhaar Card"
        elif "driving" in text_lower and ("licence" in text_lower or "license" in text_lower):
            self.doc_type = "Driving License"
        elif any(word in text_lower for word in ["certificate", "board", "examination", "marks"]):
            if any(word in text_lower for word in ["secondary", "senior", "class", "cbse", "icse", "board"]):
                self.doc_type = "Board Certificate"
        else:
            self.doc_type = "Unknown Document"

        return self.doc_type

    def clean_text(self, text):
        text = re.sub(r'[^\w\s/\-,.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_pan_details(self):
        data = {}
        pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', self.text)
        if pan_match:
            data['PAN Number'] = pan_match.group()

        name_match = re.search(r'(?:Name|NAME)\s*[:\-]?\s*([A-Z][A-Za-z\s]+?)(?:\n|Date|DOB|Father)', self.text)
        if name_match:
            data['Name'] = self.clean_text(name_match.group(1))

        father_match = re.search(
            r'(?:Father\'?s?\s*Name|FATHER\'?S?\s*NAME)\s*[:\-]?\s*([A-Z][A-Za-z\s]+?)(?:\n|Date|DOB)', self.text)
        if father_match:
            data['Father\'s Name'] = self.clean_text(father_match.group(1))

        dob_match = re.search(r'(?:Date of Birth|DOB|Birth)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})', self.text,
                              re.IGNORECASE)
        if dob_match:
            data['Date of Birth'] = dob_match.group(1)

        return data

    def extract_aadhaar_details(self):
        data = {}

        aadhaar_patterns = [
            r'\b(\d{4})\s+(\d{4})\s+(\d{4})\b',
            r'\b(\d{4})(\d{4})(\d{4})\b'
        ]

        for pattern in aadhaar_patterns:
            matches = re.findall(pattern, self.text)
            for match in matches:
                if isinstance(match, tuple):
                    aadhaar = ''.join(match)
                else:
                    aadhaar = match.replace(' ', '')

                if len(aadhaar) == 12 and aadhaar.isdigit():
                    data['Aadhaar Number'] = f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}"
                    break
            if 'Aadhaar Number' in data:
                break

        lines = self.text.split('\n')
        potential_names = []

        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 5 and len(line_clean) < 50:
                if re.match(r'^[A-Z][A-Za-z\s]+$', line_clean):
                    exclude_words = ['GOVERNMENT', 'INDIA', 'UNIQUE', 'UIDAI', 'MALE', 'FEMALE', 'ADDRESS', 'AADHAAR',
                                     'DOB', 'YEAR', 'BIRTH']
                    if not any(word in line_clean.upper() for word in exclude_words):
                        potential_names.append(line_clean)

        if potential_names:
            data['Name'] = potential_names[0]

        dob_patterns = [
            r'(?:DOB|Birth|YOB|Date of Birth)[:\s]*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',
            r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b',
            r'(?:DOB|Birth|YOB)[:\s]*(\d{4})'
        ]

        for pattern in dob_patterns:
            dob_match = re.search(pattern, self.text, re.IGNORECASE)
            if dob_match:
                dob = dob_match.group(1)
                if '/' in dob or '-' in dob or '.' in dob:
                    data['Date of Birth'] = dob
                    break

        if re.search(r'\b[Mm]ale\b', self.text):
            data['Gender'] = 'Male'
        elif re.search(r'\b[Ff]emale\b', self.text):
            data['Gender'] = 'Female'

        so_match = re.search(r'S/O[:\s]*([A-Z][A-Za-z\s]+?)(?:\n|,|\d)', self.text, re.IGNORECASE)
        if so_match:
            data['Father/Husband Name'] = self.clean_text(so_match.group(1))

        address_patterns = [
            r'(?:Address|ADDRESS)[:\s]*(.*?)(?=\n.*?(?:Aadhaar|proof|identity|citizenship))',
            r'[A-Z]\s*/\s*[A-Z].*?,.*?\d{6}',
            r'(?:Colony|Nagar|Road|Street|Gali).*?\d{6}'
        ]

        for pattern in address_patterns:
            address_match = re.search(pattern, self.text, re.DOTALL | re.IGNORECASE)
            if address_match:
                address = self.clean_text(
                    address_match.group(1) if len(address_match.groups()) > 0 else address_match.group())
                if len(address) > 15:
                    data['Address'] = address
                    break

        pincode_match = re.search(r'\b(\d{6})\b', self.text)
        if pincode_match:
            data['Pincode'] = pincode_match.group(1)

        return data

    def extract_driving_license_details(self):
        data = {}

        for pattern in [r'\b[A-Z]{2}[-/\s]?\d{2}[-/\s]?\d{4}[-/\s]?\d{7}\b', r'\b[A-Z]{2}\d{13,14}\b']:
            dl_match = re.search(pattern, self.text)
            if dl_match:
                data['License Number'] = dl_match.group()
                break

        name_match = re.search(r'(?:Name|NAME)[:\s]*([A-Z][A-Za-z\s]+?)(?:\n|S/O|D/O|W/O)', self.text)
        if name_match:
            data['Name'] = self.clean_text(name_match.group(1))

        dob_match = re.search(r'(?:DOB|Date of Birth|Birth)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})', self.text, re.IGNORECASE)
        if dob_match:
            data['Date of Birth'] = dob_match.group(1)

        issue_match = re.search(r'(?:Issue|Issued|DOI)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})', self.text, re.IGNORECASE)
        if issue_match:
            data['Date of Issue'] = issue_match.group(1)

        for pattern in [r'(?:Valid Till|Validity|Valid Upto|Expiry)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})',
                        r'(?:NT|Transport)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})']:
            validity_match = re.search(pattern, self.text, re.IGNORECASE)
            if validity_match:
                data['Valid Till'] = validity_match.group(1)
                break

        bg_match = re.search(r'\b(A\+|A-|B\+|B-|AB\+|AB-|O\+|O-)\b', self.text)
        if bg_match:
            data['Blood Group'] = bg_match.group(1)

        return data

    def extract_board_certificate_details(self):
        data = {}

        name_match = re.search(
            r'(?:Name of (?:the )?Candidate|Student\'?s? Name|NAME)[:\s]*([A-Z][A-Za-z\s]+?)(?:\n|Mother|Father|Roll)',
            self.text, re.IGNORECASE)
        if name_match:
            data['Student Name'] = self.clean_text(name_match.group(1))

        for pattern in [r'(?:Roll No|Roll Number|Enrollment No)[:\.\s]*([A-Z0-9]+)', r'\b\d{7,10}\b']:
            roll_match = re.search(pattern, self.text, re.IGNORECASE)
            if roll_match:
                data['Roll Number'] = roll_match.group(1).strip()
                break

        dob_match = re.search(r'(?:Date of Birth|DOB|Birth)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})', self.text, re.IGNORECASE)
        if dob_match:
            data['Date of Birth'] = dob_match.group(1)

        exam_match = re.search(r'(?:Examination|Exam)[:\s]*([A-Za-z]+\s*\d{4})', self.text, re.IGNORECASE)
        if exam_match:
            data['Examination'] = exam_match.group(1)

        for pattern in [r'(?:Percentage|%)[:\s]*(\d{1,3}\.\d{1,2})', r'\b(\d{1,3}\.\d{1,2})%',
                        r'(?:Grade|CGPA)[:\s]*([A-Z0-9+\.\-]+)']:
            perc_match = re.search(pattern, self.text, re.IGNORECASE)
            if perc_match:
                data['Marks/Grade'] = perc_match.group(1)
                break

        if re.search(r'\bPASS\b|\bPassed\b', self.text, re.IGNORECASE):
            data['Result'] = 'PASS'
        elif re.search(r'\bFAIL\b|\bFailed\b', self.text, re.IGNORECASE):
            data['Result'] = 'FAIL'

        return data

    def process_document(self):
        print(f"Processing document: {self.file_path}")
        print("=" * 50)

        self.extract_text()
        doc_type = self.identify_document_type()
        print(f"Document Type: {doc_type}\n")

        if doc_type == "PAN Card":
            self.extracted_data = self.extract_pan_details()
        elif doc_type == "Aadhaar Card":
            self.extracted_data = self.extract_aadhaar_details()
        elif doc_type == "Driving License":
            self.extracted_data = self.extract_driving_license_details()
        elif doc_type == "Board Certificate":
            self.extracted_data = self.extract_board_certificate_details()
        else:
            print("Unable to identify document type or unsupported document.")
            return

        print("Extracted Details:")
        print("-" * 50)
        for key, value in self.extracted_data.items():
            print(f"{key}: {value}")

        if not self.extracted_data:
            print("No details could be extracted. Please ensure the file is clear.")

        return self.extracted_data


if __name__ == "__main__":
    print("=" * 50)
    print("ID Document Scanner (Images & PDFs)")
    print("=" * 50)

    file_path = input("\nEnter the path to your document (image or PDF): ").strip()
    file_path = file_path.replace('"', '').replace("'", '')

    if not os.path.exists(file_path):
        print(f"\nError: File not found at '{file_path}'")
        print("\nTroubleshooting:")
        print("1. Make sure the file path is correct")
        print("2. Use full path like: C:/Users/YourName/Documents/document.pdf")
        print("3. Or place the file in the same folder as this script")
        print("4. Supported formats: .jpg, .jpeg, .png, .bmp, .tiff, .pdf")
        exit()

    file_ext = os.path.splitext(file_path)[1].lower()
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf']

    if file_ext not in supported_formats:
        print(f"\nError: Unsupported file format '{file_ext}'")
        print(f"Supported formats: {', '.join(supported_formats)}")
        exit()

    try:
        print(f"\nFile found! Processing...")
        scanner = IDDocumentScanner(file_path)

        if scanner.image is None:
            print("\nError: Could not read the file. Make sure it's valid.")
            exit()

        result = scanner.process_document()

        print("\n" + "=" * 50)
        print("Processing Complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\nError processing document: {str(e)}")
        print("\nPossible issues:")
        print("1. Tesseract OCR is not installed")
        print("2. For PDFs: poppler is not installed")
        print("3. File quality is too poor")
        print("4. Required library missing - run: pip install Pillow")




