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
from PIL import Image, ImageOps
import pytesseract
from typing import Dict, Any, List, Optional, Tuple
import re
from dataclasses import dataclass
from pdf2image import convert_from_bytes

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

def _auto_rotate(im: Image.Image) -> Image.Image:
    """Auto-rotate image based on OSD data from Tesseract."""
    try:
        osd = pytesseract.image_to_osd(im)
        angle = int(re.search(r"Rotate: (\d+)", osd).group(1))
        if angle and angle % 360 != 0:
            im = im.rotate(-angle, expand=True)
    except Exception:
        pass
    return im

def _preprocess(im: Image.Image) -> Image.Image:
    """Preprocess image for better OCR results."""
    # grayscale, denoise, adaptive binarize, mild sharpen
    cv = _to_cv(im)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=8)
    bw = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 35, 11)
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharp = cv2.filter2D(bw, -1, kernel)
    return _from_cv(cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR))

def _ocr(im: Image.Image, lang: str = "eng+deu",
         psm: int = 6) -> Tuple[str, List[Dict[str, Any]]]:
    """Perform OCR on the image, returning full text and word-level data.
    Can later be extended with more languages or custom configs.
    """
    # OCR config
    cfg = f"--oem 3 --psm {psm}" # Default OCR Engine Mode 3 (LSTM+Legacy), Page Segmentation Mode

    # Full text    
    txt = pytesseract.image_to_string(im, lang=lang, config=cfg)

    # Word-level data with bounding boxes and confidence
    tsv = pytesseract.image_to_data(im, lang=lang, config=cfg, output_type=pytesseract.Output.DICT)
    
    # Collect words with positive confidence
    words = []
    for i in range(len(tsv["text"])):
        if int(tsv["conf"][i]) >= 0 and tsv["text"][i].strip():
            words.append({
                "text": tsv["text"][i],                                                         # word text
                "conf": float(tsv["conf"][i]),                                                  # confidence
                "bbox": [tsv["left"][i], tsv["top"][i], tsv["width"][i], tsv["height"][i]]      # bounding box
            })
    return txt, words

#=== Doc classifiers (very light heuristics) =============================

# MRZ line pattern for passports (TD3: 2 lines of 44 chars, A-Z0-9 and <)
PASSPORT_MRZ_LINE = re.compile(r"^[A-Z0-9<]{30,44}$")

# Hints for document classification
PASSPORT_HINTS = {"passport", "reisepass", "passeport", "passport no", "passnummer", "staat", "nationality"}
DIPLOMA_HINTS_DE = {"zeugnis", "hochschule", "universität", "fachhochschule", "abschluss", "urkunde", "diplom"}
DIPLOMA_HINTS_EN = {"diploma", "degree", "university", "college", "certificate", "transcript"}  # transcript only as hint

#=== Document classification =============================================
def classify_doc(ocr_text: str) -> str:
    """Classify document type based on OCR text content."""
    text = ocr_text.lower()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # MRZ detection: two consecutive lines of dense < and A-Z0-9 (~44 chars) is strong passport signal
    dense_lines = [l.replace(" ", "").replace("\n", "").replace("\r", "").replace("|","") for l in lines]
    for i in range(len(dense_lines)-1):
        if PASSPORT_MRZ_LINE.match(dense_lines[i]) and PASSPORT_MRZ_LINE.match(dense_lines[i+1]):
            return "passport"
    if any(h in text for h in PASSPORT_HINTS):
        return "passport"
    if any(h in text for h in DIPLOMA_HINTS_DE | DIPLOMA_HINTS_EN):
        return "diploma"
    return "unknown"

#=== Field extraction ==================================================

# Date pattern: YYYY-MM-DD or DD-MM-YYYY with - . / separators
DATE_RE = re.compile(r"(?:(?:19|20)\d{2}[-./](?:0?[1-9]|1[0-2])[-./](?:0?[1-9]|[12]\d|3[01]))|"
                     r"(?:(?:0?[1-9]|[12]\d|3[01])[-./](?:0?[1-9]|1[0-2])[-./](?:19|20)\d{2})")

# MRZ TD3 parser (2 lines, 44 chars each) – tolerant cleanup
def _extract_passport_from_mrz(text: str) -> Dict[str, Any]:
    """Extract passport fields from MRZ lines in OCR text."""
    raw_lines = [l.strip() for l in text.splitlines() if l.strip()]
    lines = []
    for l in raw_lines:
        s = re.sub(r"[^A-Z0-9<]", "", l.upper())
        if PASSPORT_MRZ_LINE.match(s):
            lines.append(s)
    # choose the *last* two matching lines (often down at page bottom)
    if len(lines) >= 2:
        l1, l2 = lines[-2], lines[-1]
        # TD3 layout:
        # L1: P<CCNAME<<GIVEN<<<<<<<<<<<<<<<<<<<<<<<<
        # L2: PASSPORTNO<CHECK>CCYYMMDD<CHECK>SEX EXP<CHK>NatID<CHK> <<optional
        out = {"mrz_line1": l1, "mrz_line2": l2}
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
    return {}

def extract_passport_fields(ocr_text: str) -> Dict[str, Any]:
    """Extract passport fields from OCR text."""
    data = _extract_passport_from_mrz(ocr_text)
    # Fallback: try to find explicit labels in body text (very rough)
    if "passport_number" not in data:
        m = re.search(r"(passport|passnummer|passport no)\s*[:\-]?\s*([A-Z0-9]{6,})", ocr_text, re.I)
        if m: data["passport_number"] = m.group(2)
    # attempt dates
    dates = DATE_RE.findall(ocr_text)
    if dates:
        data.setdefault("dates_detected", list({d for d in dates if isinstance(d, str) and d.strip()}))
    return data

# Diploma field extraction
# Person name pattern: look for labels like "Name:", "Inhaber:", etc.
PERSON_NAME_RE = re.compile(r"(name|inhaber|inhaberin|holder|graduate)[:\s]+([A-ZÄÖÜ][^\n,;]{2,70})", re.I)
# Degree type pattern
DEGREE_RE = re.compile(r"(Diplom|Bachelor|Master|Magister|Staatsexamen|Doctor|Doktor|PhD)", re.I)

def extract_diploma_fields(ocr_text: str) -> Dict[str, Any]:
    """Extract diploma fields from OCR text."""
    out: Dict[str, Any] = {}
    # likely institution (first lines often contain it)
    lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]
    if lines:
        out["institution_guess"] = lines[0][:120]
    m_name = PERSON_NAME_RE.search(ocr_text)
    if m_name:
        out["holder_name_guess"] = m_name.group(2).strip()
    m_degree = DEGREE_RE.search(ocr_text)
    if m_degree:
        out["degree_type_guess"] = m_degree.group(0)
    dates = DATE_RE.findall(ocr_text)
    if dates:
        out["dates_detected"] = list({d for d in dates if isinstance(d, str) and d.strip()})
    # simple “is certified copy?” heuristic
    out["is_copy_hint"] = bool(re.search(r"(beglaubigt|certified copy|amtlich beglaubigt)", ocr_text, re.I))
    return out

#=== Public API ===================================================================

@dataclass
class OcrResult:
    """Result of OCR analysis.
    Contains document type, full text, extracted fields, word-level data.
    JSON-serializable.
    """
    doc_type: str
    text: str
    fields: Dict[str, Any]
    words: List[Dict[str, Any]]


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

    im = _auto_rotate(im)
    pim = _preprocess(im)
    text, words = _ocr(pim, lang="eng+deu", psm=6)
    doc_type = classify_doc(text)
    fields = {}

    if doc_type == "passport":
        fields = extract_passport_fields(text)
    elif doc_type == "diploma":
        fields = extract_diploma_fields(text)

    return OcrResult(doc_type=doc_type, text=text, fields=fields, words=words)