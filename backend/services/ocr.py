#****************************************************************************
#    Application:   Annerkennung Ai Cockpit
#    Module:        services.ocr         
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports =============================================================
import io
import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Dict, Any
import re
from dataclasses import dataclass
from pdf2image import convert_from_bytes
import pathlib

#=== Helpers =============================================================
def _load_image_from_bytes(b: bytes) -> Image.Image:
    """Load image from bytes, normalize mode to RGB or L as PIL Image."""
    im = Image.open(io.BytesIO(b))
    if im.mode not in ("RGB", "L"):  # normalize
        im = im.convert("RGB")
    return im

def _to_cv(im: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR format."""
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

def _from_cv(arr: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR format to PIL Image."""
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))

def preprocess_image(im: Image.Image) -> np.ndarray:
    """Preprocess image for better OCR results.
    :param image_path: Path to the image file.
    :return: Preprocessed image as a NumPy array.
    """
    # read image
    im = _to_cv(im)
    
    # Gray
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=8)

    return denoised

def _ocr_predictions(preprocessed_im: np.ndarray, lang: str = "eng+deu",
         psm: int = 11) -> list:
    """Perform OCR on the given image.
    :param preprocessed_im: Preprocessed image as a NumPy array.
    :param lang: Languages for Tesseract OCR. 
    :param psm: Page segmentation mode for Tesseract OCR. 
    :return: List of recognized text strings.
    """
    # config for OCR
    cfg = f"--oem 3 --psm {psm}"

    # Perform OCR
    df = pytesseract.image_to_data(
        preprocessed_im, lang=lang, config=cfg, output_type=pytesseract.Output.DATAFRAME)

    # clean dataframe
    df = df.dropna(subset=['text']) # remove rows with NaN text
    df = df[df['text'].str.strip() != ''] # remove empty text
    df = df.reset_index(drop=True) # reset index

    # check confidence and filter
    df = df[df['conf'] >= 0] # keep only confident predictions

    # lowercase all predictions
    df['text'] = df['text'].str.lower()

    # prediction list
    all_predictions = df["text"].to_list() # list of all predicted text
    return all_predictions

def _ocr_text(preprocessed_im: np.ndarray, lang: str = "eng+deu",
         psm: int = 3) -> str:
    """Perform OCR on the given image and return full text.
    :param preprocessed_im: Preprocessed image as a NumPy array.
    :param lang: Languages for Tesseract OCR. 
    :param psm: Page segmentation mode for Tesseract OCR. 
    :return: Recognized text as a single string.
    """
    # config for OCR
    cfg = f"--oem 3 --psm {psm}"
    # Perform OCR
    text = pytesseract.image_to_string(preprocessed_im, lang=lang, config=cfg)
    return text    


def detect_mrz_lines(all_predictions: list) -> list:
    """Detect MRZ lines from OCR predictions.
    :param all_predictions: List of recognized text strings.
    :return: List of detected MRZ lines.
    """
    mrz_lines = []
    
    # look for lines with at least 3 '<' characters
    for line in all_predictions:
        if line.count('<') >= 3:
            mrz_lines.append(line)

    return mrz_lines


#=== Doc classifiers (very light heuristics) =============================

# Hints for document classification
PASSPORT_HINTS = {"passport", "reisepass", "passeport", "passport no", "passnummer", "staat", "nationality"}
DIPLOMA_HINTS_DE = {"zeugnis", "hochschule", "universität", "fachhochschule", "abschluss", "urkunde", "diplom"}
DIPLOMA_HINTS_EN = {"diploma", "degree", "university", "college", "certificate", "transcript"}  # transcript only as hint

#=== Document classification =============================================
def classify_doc(predictions: list) -> str:
    """Classify document type based on OCR text content."""
    # MRZ detection
    mrz_lines = detect_mrz_lines(predictions)
    if len(mrz_lines) > 0:
        return "passport"
    if any(h in predictions for h in PASSPORT_HINTS):
        return "passport"
    if any(h in predictions for h in DIPLOMA_HINTS_DE | DIPLOMA_HINTS_EN):
        return "diploma"
    return "unknown"

#=== Field extraction ==================================================

# Date pattern: YYYY-MM-DD or DD-MM-YYYY with - . / separators
DATE_RE = re.compile(r"(?:(?:19|20)\d{2}[-./](?:0?[1-9]|1[0-2])[-./](?:0?[1-9]|[12]\d|3[01]))|"
                     r"(?:(?:0?[1-9]|[12]\d|3[01])[-./](?:0?[1-9]|1[0-2])[-./](?:19|20)\d{2})")

# MRZ TD3 parser (2 lines, 44 chars each) – tolerant cleanup
def _extract_passport_data_from_mrz(mrz_lines: list) -> Dict[str, Any]:
    """Extract passport fields from MRZ lines in OCR text.
    :param mrz_lines: List of OCR text lines.
    :return: Dictionary of extracted fields.
    """
    out: Dict[str, Any] = {}

    # TD3 layout:
    # L1: P<CCNAME<<GIVEN<<<<<<<<<<<<<<<<<<<<<<<<
    # L2: PASSPORTNO<CHECK>CCYYMMDD<CHECK>SEX EXP<CHK>NatID<CHK> <<optional
    if len(mrz_lines) == 2:
        # Clean lines and uppercase
        l1 = mrz_lines[0].replace(" ", "").upper()
        l2 = mrz_lines[1].replace(" ", "").upper()
        
        # Add to output
        out = {"mrz_line1": l1, "mrz_line2": l2}

        # Parse fields
        try:
            # Extract fields based on fixed positions
            out["document_code"] = l1[0:2]
            out["issuing_country"] = l1[2:5]
            name_raw = l1[5:].split("<<", 1)
            out["surname"] = name_raw[0].replace("<", " ").strip()
            out["given_names"] = name_raw[1].replace("<", " ").strip() if len(name_raw)>1 else ""
            out["passport_number"] = l2[0:9].replace("<","").strip()
            out["nationality"]     = l2[10:13]
            out["birth_date_raw"]  = l2[13:19]   # YYMMDD
            out["sex"]             = l2[20:21]
            out["expiry_date_raw"] = l2[21:27]   # YYMMDD
        except Exception:
            pass
    return out

def extract_passport_fields(predictions: list) -> Dict[str, Any]:
    """Extract passport fields from OCR predictions list.
    :param predictions: List of recognized text strings.
    :return: Dictionary of extracted fields.
    """
    passport_data = _extract_passport_data_from_mrz(detect_mrz_lines(predictions))
    ocr_text = "\n".join(predictions)
    # Fallback: try to find explicit labels in body text (very rough)
    if "passport_number" not in passport_data:
        m = re.search(r"(passport|passnummer|passport no)\s*[:\-]?\s*([A-Z0-9]{6,})", ocr_text, re.I)
        if m: passport_data["passport_number"] = m.group(2)
    return passport_data

# Diploma field extraction
# Person name pattern: look for labels like "Name:", "Inhaber:", etc.
PERSON_NAME_RE = re.compile(r"(name|inhaber|inhaberin|holder|graduate)[:\s]+([A-ZÄÖÜ][^\n,;]{2,70})", re.I)
# Degree type pattern
DEGREE_RE = re.compile(r"(Urkunde|Diplom|Bachelor|Master|Magister|Staatsexamen|Doctor|Doktor|PhD)", re.I)

def extract_diploma_fields(ocr_text: str) -> Dict[str, Any]:
    """Extract diploma fields from OCR text."""
    # take other psm for ocr
    out: Dict[str, Any] = {}
    # likely institution (first lines often contain it
    lines = ocr_text.splitlines()
    if lines:
        out["institution_guess"] = lines[0].strip()
    # holder name
    m = PERSON_NAME_RE.search(ocr_text)
    if m:
        out["holder_name_guess"] = m.group(2).strip()
    # degree type
    m = DEGREE_RE.search(ocr_text)
    if m:
        out["degree_type_guess"] = m.group(1).strip()
    # dates
    dates = DATE_RE.findall(ocr_text)
    if dates:
        out["dates_detected"] = dates
    # certified copy hint
    if re.search(r"(certified copy|beglaubigte kopie|beglaubigung|copy)", ocr_text, re.I):
        out["is_certified_copy_hint"] = True

    return out

#=== Public API ===================================================================

@dataclass
class OcrResult:
    """Result of OCR analysis.
    Contains document type, full text, extracted fields, word-level data.
    JSON-serializable.
    """
    doc_type: str
    predictions: list
    ocr_text: str
    fields: Dict[str, Any]


def analyze_bytes(file_bytes: bytes) -> OcrResult:
    # Detect file type
    if file_bytes[:4] == b'%PDF':  # quick check for PDF magic number
        # Convert PDF pages to images
        pages = convert_from_bytes(file_bytes, dpi=300)  # 300 dpi for decent OCR quality
        if not pages:
            raise ValueError("Empty PDF")
        # Take the first page for PoC (you can loop later)
        im = pages[0]
    else:
        im = _load_image_from_bytes(file_bytes)

    pim = preprocess_image(im)
    predictions = _ocr_predictions(pim)
    ocr_text = _ocr_text(im, psm=6)
    print(ocr_text)
    doc_type = classify_doc(predictions)
    fields = {}

    if doc_type == "passport":
        fields = extract_passport_fields(predictions)
        ocr_text = "\n".join(predictions)
    elif doc_type == "diploma":
        pass
        fields = extract_diploma_fields(ocr_text)
        predictions = ocr_text.splitlines()
        
    return OcrResult(doc_type=doc_type, predictions=predictions, ocr_text=ocr_text, fields=fields)

image_path = "/home/chief/Projects/anerkennung_ai_cockpit/dummy_docs/id_HM.jpg"

p = pathlib.Path(image_path)
b = p.read_bytes()
res = analyze_bytes(b)
print(res)