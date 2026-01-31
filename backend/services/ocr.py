#****************************************************************************
#    Application:   Annerkennung Ai Cockpit
#    Module:        services.ocr         
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports =============================================================
import io
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Dict, Any
import re
from dataclasses import dataclass
from pdf2image import convert_from_bytes
import pathlib
import json
try:
    from caesar_ocr import analyze_bytes as caesar_analyze_bytes
    from caesar_ocr.regex.engine import load_rules as caesar_load_rules, run_rules as caesar_run_rules
    from caesar_ocr.pipeline.analyze import analyze_document_bytes as caesar_analyze_document_bytes
except Exception:
    caesar_analyze_bytes = None
    caesar_load_rules = None
    caesar_run_rules = None
    caesar_analyze_document_bytes = None

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

def _ensure_tesseract_env() -> None:
    if not os.environ.get("TESSDATA_PREFIX"):
        candidates = [
            "/app/.apt/usr/share/tesseract-ocr/5/tessdata",
            "/app/.apt/usr/share/tesseract-ocr/4.00/tessdata",
            "/app/.apt/usr/share/tessdata",
            "/usr/share/tesseract-ocr/5/tessdata",
            "/usr/share/tesseract-ocr/4.00/tessdata",
        ]
        for path in candidates:
            if os.path.isdir(path):
                os.environ["TESSDATA_PREFIX"] = path
                break
        if os.environ.get("DYNO"):
            os.environ.setdefault("TESSDATA_PREFIX", "/app/.apt/usr/share/tesseract-ocr/5/tessdata")
    tesseract_bin = "/app/.apt/usr/bin/tesseract"
    if os.path.isfile(tesseract_bin):
        pytesseract.pytesseract.tesseract_cmd = tesseract_bin

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


def _ocr_mrz(im: Image.Image) -> str:
    """
    OCR only the bottom strip of the document to improve MRZ extraction.
    """
    try:
        w, h = im.size
        # bottom ~25% of the page
        crop = im.crop((0, int(h * 0.75), w, h))
        crop = crop.convert("L")
        arr = np.array(crop)
        # binarize for MRZ
        _, th = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _ensure_tesseract_env()
        cfg = "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
        return pytesseract.image_to_string(th, lang="eng", config=cfg)
    except Exception:
        return ""

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

    _ensure_tesseract_env()
    try:
        # Perform OCR
        df = pytesseract.image_to_data(
            preprocessed_im, lang=lang, config=cfg, output_type=pytesseract.Output.DATAFRAME)
    except Exception:
        return []

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
    _ensure_tesseract_env()
    try:
        # Perform OCR
        text = pytesseract.image_to_string(preprocessed_im, lang=lang, config=cfg)
        return text
    except Exception:
        return ""   


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
        return "Passport"
    if any(h in predictions for h in PASSPORT_HINTS):
        return "Passport"
    if any(h in predictions for h in DIPLOMA_HINTS_DE | DIPLOMA_HINTS_EN):
        return "Degree Certificate"
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
    _ensure_tesseract_env()
    if caesar_analyze_bytes is not None:
        res = caesar_analyze_bytes(file_bytes, lang="eng+deu")
        rules_paths = _resolve_rules_paths(file_bytes)
        if rules_paths and caesar_load_rules is not None and caesar_run_rules is not None:
            for rules_path in rules_paths:
                rules_file = pathlib.Path(rules_path)
                if not rules_file.exists():
                    continue
                rules = caesar_load_rules(rules_file)
                regex_fields = caesar_run_rules(res.ocr_text, rules, debug=False)
                if regex_fields:
                    res.fields.update(regex_fields)
        _apply_doc_type_hints(res)
        return OcrResult(
            doc_type=res.doc_type,
            predictions=res.predictions,
            ocr_text=res.ocr_text,
            fields=res.fields,
        )
    # Detect file type
    if file_bytes[:4] == b'%PDF':  # quick check for PDF magic number
        # Convert PDF pages to images
        pages = convert_from_bytes(file_bytes, dpi=400)  # higher DPI for MRZ accuracy
        if not pages:
            raise ValueError("Empty PDF")
        # Take the first page for PoC (you can loop later)
        im = pages[0]
    else:
        im = _load_image_from_bytes(file_bytes)

    pim = preprocess_image(im)
    predictions = _ocr_predictions(pim)
    ocr_text = _ocr_text(im, psm=6)
    # Try MRZ-focused OCR on bottom strip for fallback accuracy
    mrz_text = _ocr_mrz(im)
    if mrz_text:
        ocr_text = ocr_text + "\n" + mrz_text
    print(ocr_text)
    doc_type = classify_doc(predictions)
    fields = {}

    if doc_type == "Passport":
        fields = extract_passport_fields(predictions)
    elif doc_type == "Degree Certificate":
        pass
        fields = extract_diploma_fields(ocr_text)
        predictions = ocr_text.splitlines()

    # Always try MRZ-based extraction to populate passport fields.
    if ocr_text:
        mrz_fields = _extract_mrz_from_text(ocr_text)
        if mrz_fields:
            for k, v in mrz_fields.items():
                fields.setdefault(k, v)
        
    return OcrResult(doc_type=doc_type, predictions=predictions, ocr_text=ocr_text, fields=fields)


def _resolve_rules_paths(file_bytes: bytes) -> list[str]:
    env_paths = os.getenv("CAESAR_OCR_RULES_PATH")
    if env_paths:
        return [p.strip() for p in env_paths.split(",") if p.strip()]

    rules_by_type = os.getenv("CAESAR_OCR_RULES_BY_TYPE")
    if rules_by_type:
        file_kind = "pdf" if file_bytes[:4] == b"%PDF" else "image"
        mapping = {}
        for part in rules_by_type.split(";"):
            if not part.strip() or "=" not in part:
                continue
            key, val = part.split("=", 1)
            mapping[key.strip().lower()] = [p.strip() for p in val.split(",") if p.strip()]
        if file_kind in mapping:
            return mapping[file_kind]

    base = pathlib.Path(__file__).resolve().parents[2] / "backend" / "utils" / "ocr_rules"
    return [str(base / "passport.yaml"), str(base / "diploma.yaml")]


def _apply_doc_type_hints(res) -> None:
    if getattr(res, "doc_type", "unknown") != "unknown":
        return
    fields = getattr(res, "fields", {}) or {}
    if "mrz_line1" in fields or "mrz_line2" in fields:
        res.doc_type = "Passport"
        return
    hint = str(fields.get("doc_type_hint", "")).lower()
    if any(k in hint for k in ("passport", "reisepass", "passeport", "mrz")):
        res.doc_type = "Passport"
        return
    if any(k in hint for k in ("diplom", "abschluss", "hochschule", "universit", "zeugnis", "degree")):
        res.doc_type = "Degree Certificate"
        return
    if "degree_type" in fields or "holder_name" in fields:
        res.doc_type = "Degree Certificate"


def analyze_bytes_with_layoutlm_fields(
    file_bytes: bytes,
    *,
    lang: str = "eng+deu",
    token_model_dir: str | None = None,
) -> tuple[OcrResult, dict]:
    """
    Run OCR and, if LayoutLM token model is configured, extract labeled fields.
    Returns (ocr_result, extracted_fields).
    """
    if caesar_analyze_document_bytes is None:
        res = analyze_bytes(file_bytes)
        if res.ocr_text:
            res.fields.update(_extract_mrz_from_text(res.ocr_text))
            res.fields = _postprocess_passport_fields(res.fields)
        return res, res.fields or {}

    token_model_dir = token_model_dir or os.getenv("CAESAR_LAYOUTLM_TOKEN_MODEL_DIR")
    if not token_model_dir:
        res = analyze_bytes(file_bytes)
        if res.ocr_text:
            res.fields.update(_extract_mrz_from_text(res.ocr_text))
            res.fields = _postprocess_passport_fields(res.fields)
        return res, res.fields or {}

    regex_paths = _resolve_rules_paths(file_bytes)
    regex_path = regex_paths[0] if regex_paths else None

    tool_res = caesar_analyze_document_bytes(
        file_bytes,
        layoutlm_model_dir=os.getenv("CAESAR_LAYOUTLM_MODEL_DIR"),
        layoutlm_token_model_dir=token_model_dir,
        lang=lang,
        layoutlm_lang=os.getenv("CAESAR_LAYOUTLM_LANG"),
        regex_rules_path=regex_path,
        regex_debug=False,
    )
    res = tool_res.ocr

    label_map = _load_label_map()
    labeled_fields = _extract_fields_from_labeled_tokens(tool_res.schema, label_map)
    if labeled_fields:
        res.fields.update(labeled_fields)
        _apply_doc_type_hints(res)

    if res.ocr_text:
        # Fill any missing MRZ fields from OCR text.
        mrz_fields = _extract_mrz_from_text(res.ocr_text)
        for k, v in mrz_fields.items():
            res.fields.setdefault(k, v)
        res.fields = _postprocess_passport_fields(res.fields)

    return res, res.fields or {}


def _load_label_map() -> dict:
    """
    Load label mapping for LayoutLM token labels to field names.
    """
    map_path = os.getenv("CAESAR_PASSPORT_LABEL_MAP_PATH")
    if not map_path:
        map_path = str(
            pathlib.Path(__file__).resolve().parents[2]
            / "backend"
            / "utils"
            / "label_maps"
            / "passport.json"
        )
    try:
        with open(map_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _extract_fields_from_labeled_tokens(schema, label_map: dict) -> dict:
    if schema is None:
        return {}

    fields: dict[str, list[str]] = {}

    pages = getattr(schema, "ocr", None)
    if pages is None:
        return {}
    page_items = getattr(pages, "pages", None)
    if not page_items:
        return {}

    for page in page_items:
        for token in getattr(page, "tokens", []) or []:
            label = token.label
            text = token.text
            if not label or label == "O" or not text:
                continue
            label_clean = label.replace("B-", "").replace("I-", "")
            field_key = label_map.get(label_clean) or label_map.get(label) or label_clean.lower()
            if field_key not in fields:
                fields[field_key] = []
            fields[field_key].append(text)

    merged = {k: " ".join(v).strip() for k, v in fields.items() if v}
    return _postprocess_passport_fields(merged)


def _postprocess_passport_fields(fields: dict) -> dict:
    """
    Normalize MRZ fields from token labels (YYMMDD -> YYYY-MM-DD) and
    derive human-friendly data when possible.
    """
    def _fix_digit_like(val: str) -> str:
        if not val:
            return val
        table = str.maketrans({"O": "0", "I": "1", "L": "1", "Z": "2", "S": "5", "B": "8"})
        return val.upper().translate(table)

    def _fix_alpha_like(val: str) -> str:
        if not val:
            return val
        table = str.maketrans({"0": "O", "1": "I", "2": "Z", "5": "S", "8": "B"})
        return val.upper().translate(table)

    def _yyMMdd_to_iso(val: str) -> str:
        if not val:
            return val
        val = _fix_digit_like(val)
        digits = "".join(ch for ch in val if ch.isdigit())
        if len(digits) != 6:
            return val
        yy = int(digits[0:2])
        mm = digits[2:4]
        dd = digits[4:6]
        # heuristic century: 00-29 => 2000s, else 1900s
        century = 2000 if yy <= 29 else 1900
        return f"{century + yy:04d}-{mm}-{dd}"

    for key in ("birth_date_raw", "expiry_date_raw"):
        if key in fields and fields[key]:
            fields[key] = _fix_digit_like(fields[key])

    for key in ("birth_date", "expiry_date"):
        if key in fields and fields[key]:
            fields[key] = _yyMMdd_to_iso(fields[key])
        raw_key = f"{key}_raw"
        if (key not in fields or not fields[key]) and raw_key in fields:
            fields[key] = _yyMMdd_to_iso(fields[raw_key])

    # Compose full name if parts exist
    if "surname" in fields or "given_names" in fields:
        surname = fields.get("surname", "")
        given = fields.get("given_names", "")
        surname = " ".join(re.sub(r"[^A-Za-zÄÖÜäöüß\\s-]", " ", surname).split())
        given = " ".join(re.sub(r"[^A-Za-zÄÖÜäöüß\\s-]", " ", given).split())
        fields["surname"] = surname
        fields["given_names"] = given
        full = " ".join(part for part in [given, surname] if part).strip()
        if full:
            fields.setdefault("full_name", full)

    # Normalize sex field
    if "sex" in fields:
        fields["sex"] = fields["sex"].strip().upper().replace("0", "O")
        if fields["sex"] not in {"M", "F", "X"}:
            fields["sex"] = ""

    for key in ("issuing_country", "nationality"):
        if key in fields and fields[key]:
            cleaned = _fix_alpha_like(fields[key])
            cleaned = "".join(ch for ch in cleaned if "A" <= ch <= "Z")
            if len(cleaned) >= 3:
                fields[key] = cleaned[:3]
            else:
                fields[key] = ""

    if "passport_number" in fields and fields["passport_number"]:
        pn = fields["passport_number"].upper().replace("<", "")
        if not re.fullmatch(r"[A-Z0-9]{6,9}", pn):
            pn_alt = _fix_digit_like(pn)
            if re.fullmatch(r"[A-Z0-9]{6,9}", pn_alt):
                pn = pn_alt
        if not re.fullmatch(r"[A-Z0-9]{6,9}", pn):
            pn = ""
        fields["passport_number"] = pn

    if "mrz_line1" in fields and fields["mrz_line1"]:
        fields["mrz_line1"] = _normalize_mrz_line(fields["mrz_line1"])
    if "mrz_line2" in fields and fields["mrz_line2"]:
        fields["mrz_line2"] = _normalize_mrz_line(fields["mrz_line2"], numeric=True)

    # Prefer MRZ-derived fields when full lines are available.
    if fields.get("mrz_line2") and len(fields["mrz_line2"]) >= 28:
        l2 = fields["mrz_line2"]
        pn = l2[0:9].replace("<", "").strip()
        nat = l2[10:13]
        braw = l2[13:19]
        sex = l2[20:21]
        eraw = l2[21:27]
        if pn:
            fields["passport_number"] = pn
        if nat:
            fields["nationality"] = _fix_alpha_like(nat)
        if braw:
            fields["birth_date"] = _yyMMdd_to_iso(braw)
            fields["birth_date_raw"] = _fix_digit_like(braw)
        if eraw:
            fields["expiry_date"] = _yyMMdd_to_iso(eraw)
            fields["expiry_date_raw"] = _fix_digit_like(eraw)
        if sex:
            sex = sex.upper().replace("0", "O")
            fields["sex"] = sex if sex in {"M", "F", "X"} else ""

    return fields


def _extract_mrz_from_text(ocr_text: str) -> dict:
    """
    Try to detect and parse MRZ lines from raw OCR text.
    """
    if not ocr_text:
        return {}

    lines = [ln.strip() for ln in ocr_text.splitlines() if ln.strip()]
    mrz_candidates = [ln for ln in lines if ln.count("<") >= 3]
    if len(mrz_candidates) >= 2:
        mrz_lines = mrz_candidates[:2]
    else:
        # Fallback: try to find a single long MRZ block and split
        joined = " ".join(lines)
        parts = [p for p in joined.split() if p.count("<") >= 3]
        if len(parts) >= 2:
            mrz_lines = parts[:2]
        else:
            # Look for a long MRZ-like token and split into 44/44
            candidates = [p for p in joined.split() if p.count("<") >= 3 and len(p) >= 80]
            if candidates:
                token = candidates[0]
                if len(token) >= 88:
                    mrz_lines = [token[:44], token[44:88]]
                else:
                    return {}
            else:
                # As a last resort, strip spaces and scan for a long MRZ run
                condensed = "".join(ch for ch in joined if ch.isalnum() or ch == "<")
                if len(condensed) >= 88 and condensed.count("<") >= 3:
                    mrz_lines = [condensed[:44], condensed[44:88]]
                else:
                    return {}

    mrz_lines = [_normalize_mrz_line(l) for l in mrz_lines]
    checksum_ok = _mrz_checksum_ok(mrz_lines[1]) if len(mrz_lines) > 1 else False

    parsed = _parse_mrz_lines(mrz_lines)
    if not parsed:
        # Loose fallback: try to detect MRZ lines by pattern and pad to length.
        candidates = [ln for ln in lines if "P<" in ln.replace(" ", "")]
        if len(candidates) >= 1:
            l1 = _normalize_mrz_line(candidates[0])
            line2_candidates = [ln for ln in lines if sum(ch.isdigit() for ch in ln) >= 10 and "<" in ln]
            l2_raw = line2_candidates[0] if line2_candidates else (candidates[1] if len(candidates) > 1 else "")
            l2 = _normalize_mrz_line(l2_raw)
            if l1 and l2:
                if len(l1) < 44:
                    l1 = l1.ljust(44, "<")
                if len(l2) < 44:
                    l2 = l2.ljust(44, "<")
                parsed = _parse_mrz_lines([l1, l2])
        if not parsed:
            return {}

    parsed["mrz_checksum_ok"] = checksum_ok
    return parsed


def _parse_mrz_lines(mrz_lines: list[str]) -> dict:
    """
    Parse TD3 MRZ (2 lines, 44 chars) in a tolerant way.
    """
    if len(mrz_lines) < 2:
        return {}
    l1 = mrz_lines[0].replace(" ", "").upper()
    l2 = mrz_lines[1].replace(" ", "").upper()
    out: dict[str, str] = {"mrz_line1": l1, "mrz_line2": l2}

    try:
        out["document_code"] = l1[0:2]
        out["issuing_country"] = l1[2:5]
        name_raw = l1[5:].split("<<", 1)
        out["surname"] = name_raw[0].replace("<", " ").strip()
        out["given_names"] = name_raw[1].replace("<", " ").strip() if len(name_raw) > 1 else ""
        out["passport_number"] = l2[0:9].replace("<","").strip()
        out["nationality"]     = l2[10:13]
        out["birth_date"]      = l2[13:19]
        out["sex"]             = l2[20:21]
        out["expiry_date"]     = l2[21:27]
        out["personal_number"] = l2[28:42].replace("<","").strip()
        out["passport_number_check"] = l2[9:10]
        out["birth_date_check"] = l2[19:20]
        out["expiry_date_check"] = l2[27:28]
        out["personal_number_check"] = l2[42:43]
        out["final_check"] = l2[43:44]
    except Exception:
        pass

    return out


def _normalize_mrz_line(line: str) -> str:
    cleaned = "".join(ch for ch in line.upper() if ch.isalnum() or ch == "<")
    return cleaned


def _mrz_char_value(ch: str) -> int:
    if ch.isdigit():
        return int(ch)
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 10
    return 0


def _mrz_check_digit(data: str) -> str:
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(data):
        total += _mrz_char_value(ch) * weights[i % 3]
    return str(total % 10)


def _mrz_checksum_ok(line2: str) -> bool:
    """
    Validate key check digits for TD3 line 2.
    """
    if not line2 or len(line2) < 44:
        return False
    line2 = _normalize_mrz_line(line2)
    if len(line2) < 44:
        return False

    passport_no = line2[0:9]
    passport_no_chk = line2[9:10]
    birth = line2[13:19]
    birth_chk = line2[19:20]
    expiry = line2[21:27]
    expiry_chk = line2[27:28]
    personal = line2[28:42]
    personal_chk = line2[42:43]
    final_chk = line2[43:44]

    if _mrz_check_digit(passport_no) != passport_no_chk:
        return False
    if _mrz_check_digit(birth) != birth_chk:
        return False
    if _mrz_check_digit(expiry) != expiry_chk:
        return False
    if _mrz_check_digit(personal) != personal_chk:
        return False

    composite = passport_no + passport_no_chk + line2[10:13] + birth + birth_chk + expiry + expiry_chk + personal + personal_chk
    if _mrz_check_digit(composite) != final_chk:
        return False

    return True


#image_path = "/home/chief/Projects/anerkennung_ai_cockpit/dummy_docs/id_HM.jpg"
#
#p = pathlib.Path(image_path)
#b = p.read_bytes()
#res = analyze_bytes(b)
#
