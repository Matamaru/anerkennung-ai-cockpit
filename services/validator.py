import re

CANONICAL_DOCS = {
    "Passport": ["passport", "pass", "reiseausweis"],
    "Nursing Diploma": ["diploma", "degree", "nurse_certificate"],
    "Diploma Transcript": ["transcript", "marksheet", "course_list"],
    "License/Registration": ["license", "registration", "reg", "prc"],
    "Birth Certificate": ["birth", "geburtsurkunde"],
    "CV (German)": ["cv", "lebenslauf"],
    "Proof of Language B2": ["b2", "sprachzertifikat"],
    "Proof of Language B2 Pflege": ["b2_pflege", "pflege_b2", "sprachzertifikat_pflege"],
    "Good Standing Certificate": ["good_standing", "gsc"],
    "Apostille/Legalization (if required)": ["apostille", "legalization", "legalisation"],
    "Certified Translations": ["translation", "uebersetzung", "übersetzung"],
}

def infer_present_docs(filenames):
    present = set()
    lower_files = [f.lower() for f in filenames]
    for canon, keywords in CANONICAL_DOCS.items():
        for kw in keywords:
            if any(re.search(rf"\b{re.escape(kw)}\b", f) for f in lower_files):
                present.add(canon)
                break
    return present
