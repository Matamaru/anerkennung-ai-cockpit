#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        utils.state_rules
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.2
#****************************************************************************

"""
Simple, editable checklists per Bundesland (federal state) for the
nurse recognition (Anerkennung) MVP.

This module now includes:
1. STATE_CHECKLISTS – quick static lists for fast prototyping or fallback.
2. STATE_RULES – structured, validated rulesets for production use.
3. Helper functions to retrieve and format the data for UI consumption.
"""

# ---------------------------------------------------------------------------
# BASIC CHECKLISTS (MVP fallback – plain lists for quick display)
# ---------------------------------------------------------------------------

STATE_CHECKLISTS = {
    "Berlin": [
        "Passport",
        "Nursing Diploma",
        "Diploma Transcript",
        "License/Registration",
        "Birth Certificate",
        "CV (German)",
        "Proof of Language B2",
        "Apostille/Legalization (if required)",
        "Certified Translations",
    ],
    "Bavaria": [
        "Passport",
        "Nursing Diploma",
        "Diploma Transcript",
        "License/Registration",
        "CV (German)",
        "Proof of Language B2 Pflege",
        "Good Standing Certificate",
        "Apostille/Legalization (if required)",
        "Certified Translations",
    ],
    "NRW": [
        "Passport",
        "Nursing Diploma",
        "Diploma Transcript",
        "License/Registration",
        "CV (German)",
        "Proof of Language B2",
        "Good Standing Certificate",
        "Apostille/Legalization (if required)",
        "Certified Translations",
    ],
}

# ---------------------------------------------------------------------------
# STRUCTURED STATE RULES (advanced configuration)
# ---------------------------------------------------------------------------

STATE_RULES = {}

# --- Berlin (BE) -------------------------------------------------------------
# TODO: Check for correct and complete requirements with official sources

STATE_RULES["BE"] = {
    "state_code": "BE",
    "state_label": "Berlin",
    "locale": "en-DE",
        "tone": {
        "form": "you",
        "style": "clear, calm, precise",
    },
    "sections": [
        {"key": "required", "title": "Mandatory documents"},
        {"key": "conditional", "title": "Conditional / profession-dependent documents"},
        {"key": "translations", "title": "Translations"},
        {"key": "formal", "title": "Formal details"},
    ],
    "checklist": [
        {
            "key": "id_document",
            "section": "required",
            "label": "Official ID document (passport or national ID card) - front and back sides",
            "required": True,
            "notes": "Make sure the image is straight and clearly readable.",
        },
        {
            "key": "cv",
            "section": "required",
            "label": "Curriculum Vitae (CV) - table format, up to date, and without gaps",
            "required": True,
        },
        {
            "key": "degree_certificates",
            "section": "required",
            "label": "Diploma(s) and degree certificate(s) - certified copy or original",
            "required": True,
        },
        {
            "key": "transcript",
            "section": "required",
            "label": "Transcript or list of subjects/hours, if available",
            "required": False,
        },
        {
            "key": "work_experience",
            "section": "required",
            "label": "Proof of relevant work experience (reference letters or employment certificates)",
            "required": True,
        },
        {
            "key": "data_consent",
            "section": "required",
            "label": "Power of attorney / data processing consent (if submitted by a third party)",
            "required": False,
        },
        {
            "key": "language_certificates",
            "section": "conditional",
            "label": "Language or professional certificates (e.g. B2/C1), if required",
            "required": False,
            "conditional_on": ["profession_requires_language_level"],
        },
        {
            "key": "other_licenses",
            "section": "conditional",
            "label": "Recognition or license certificates from other countries, if available",
            "required": False,
        },
        {
            "key": "name_change",
            "section": "conditional",
            "label": "Proof of name change (e.g. marriage certificate), if applicable",
            "required": False,
        },
        {
            "key": "translations",
            "section": "translations",
            "label": "Certified translations of all non-German documents",
            "required": True,
            "notes": "Must be prepared by publicly sworn translators.",
        },
        {
            "key": "contact",
            "section": "formal",
            "label": "Current contact information (address, email, phone)",
            "required": True,
        },
        {
            "key": "registration_optional",
            "section": "formal",
            "label": "Residence registration (if you have a Berlin address) - optional",
            "required": False,
        },
    ],
    "helptexts": {
        "quality": "Upload straight, clearly readable scans or photos. Include all pages.",
        "translations": "Translations must be certified by officially sworn translators.",
        "conditional": "Only upload items marked 'if applicable' when relevant to your case.",
    },
    "emails": {
        "missing_docs_subject": "Your recognition documents - missing items",
        "missing_docs_body": (
            "Dear {name},\n\n"
            "Thank you for submitting your documents. After the initial review, "
            "the following items are still missing for your Berlin submission:\n\n"
            "{missing_list}\n\n"
            "Please make sure your uploads are clearly readable and that any non-German "
            "documents are accompanied by certified translations.\n\n"
            "If you have any questions, we are happy to assist.\n"
            "Best regards,\n{signature}"
        ),
    },
    "rules": {
        "at_least_one_id": ["id_document"],
        "must_translate_if_not_de": [
            "degree_certificates",
            "transcript",
            "work_experience",
            "other_licenses",
        ],
        "require_language_if_profession_demands": {
            "flag": "profession_requires_language_level",
            "keys": ["language_certificates"],
        },
    },
}

# --- North Rhine-Westphalia / Nordrhein-Westfalen (NW) ----------------------
# TODO: Check for correct and complete requirements with official sources

STATE_RULES["NW"] = {
    "state_code": "NW",
    "state_label": "North Rhine-Westphalia (NRW)",
    "locale": "en-DE",
    "tone": {
        "form": "you",
        "style": "clear, calm, precise",
    },
    # UI sections and titles (kept identical to Berlin for consistency)
    "sections": [
        {"key": "required", "title": "Mandatory documents"},
        {"key": "conditional", "title": "Conditional / profession-dependent documents"},
        {"key": "translations", "title": "Translations"},
        {"key": "formal", "title": "Formal details"},
    ],
    # Checklist items
    "checklist": [
        {
            "key": "id_document",
            "section": "required",
            "label": "Official ID document (passport or national ID card) - front and back sides",
            "required": True,
            "notes": "Make sure the image is straight and clearly readable.",
        },
        {
            "key": "cv",
            "section": "required",
            "label": "Curriculum Vitae (CV) - table format, up to date, and without gaps",
            "required": True,
        },
        {
            "key": "degree_certificates",
            "section": "required",
            "label": "Diploma(s) and degree certificate(s) - certified copy or original",
            "required": True,
        },
        {
            "key": "transcript",
            "section": "required",
            "label": "Diploma transcript / list of subjects and hours, if available",
            "required": False,
        },
        {
            "key": "license_registration",
            "section": "required",
            "label": "Professional license / registration from home country (if applicable to your profession)",
            "required": True,
        },
        {
            "key": "work_experience",
            "section": "required",
            "label": "Proof of relevant work experience (reference letters or employment certificates)",
            "required": True,
        },
        {
            "key": "language_b2_pflege",
            "section": "required",
            "label": "Proof of language level (B2 Pflege or equivalent)",
            "required": True,
            "notes": "If Fachsprachprüfung is required, please add the certificate when available.",
        },
        {
            "key": "good_standing",
            "section": "required",
            "label": "Certificate of Good Standing / Current Professional Standing (from competent authority)",
            "required": True,
        },
        {
            "key": "apostille_legalization",
            "section": "conditional",
            "label": "Apostille or legalization on foreign public documents, if required",
            "required": False,
            "notes": "Only for documents issued outside Germany when the authority requests it.",
            "conditional_on": ["requires_apostille"],
        },
        {
            "key": "name_change",
            "section": "conditional",
            "label": "Proof of name change (e.g. marriage certificate), if applicable",
            "required": False,
        },
        {
            "key": "translations",
            "section": "translations",
            "label": "Certified translations of all non-German documents",
            "required": True,
            "notes": "Must be prepared by publicly sworn translators.",
        },
        {
            "key": "contact",
            "section": "formal",
            "label": "Current contact information (address, email, phone)",
            "required": True,
        },
    ],
    # Helper texts for UI tooltips / FAQ
    "helptexts": {
        "quality": "Upload straight, clearly readable scans or photos. Include all pages.",
        "translations": "Translations must be certified by officially sworn translators.",
        "conditional": "Only upload items marked 'if applicable' when relevant to your case.",
        "apostille": "Apostilles/legalizations may be required for foreign public documents depending on the issuing country and the authority’s instructions.",
    },
    # Email templates (English, polite tone)
    "emails": {
        "missing_docs_subject": "Your recognition documents (NRW) - missing items",
        "missing_docs_body": (
            "Dear {name},\n\n"
            "Thank you for submitting your documents. After the initial review, "
            "the following items are still missing for your NRW submission:\n\n"
            "{missing_list}\n\n"
            "Please make sure your uploads are clearly readable and that any non-German "
            "documents are accompanied by certified translations. If apostilles/legalizations "
            "are required, please attach them as well.\n\n"
            "If you have any questions, we are happy to assist.\n"
            "Best regards,\n{signature}"
        ),
    },
    # Validation rules for backend/frontend
    "rules": {
        "at_least_one_id": ["id_document"],
        "must_translate_if_not_de": [
            "degree_certificates",
            "transcript",
            "license_registration",
            "work_experience",
            "good_standing",
        ],
        "require_language_b2": ["language_b2_pflege"],
        "require_apostille_if_flag": {
            "flag": "requires_apostille",
            "keys": [
                "degree_certificates",
                "transcript",
                "license_registration",
                "good_standing",
            ],
        },
    },
}

# --- Bavaria / Bayern (BY) --------------------------------------------------
# TODO: Check for correct and complete requirements with official sources

STATE_RULES["BY"] = {
    "state_code": "BY",
    "state_label": "Bavaria (Bayern)",
    "locale": "en-DE",
    "tone": {
        "form": "you",
        "style": "clear, calm, precise",
    },
    # Same section layout as BE/NW for UI consistency
    "sections": [
        {"key": "required", "title": "Mandatory documents"},
        {"key": "conditional", "title": "Conditional / profession-dependent documents"},
        {"key": "translations", "title": "Translations"},
        {"key": "formal", "title": "Formal details"},
    ],
    # Checklist items (aligned with your MVP list for Bavaria)
    "checklist": [
        {
            "key": "id_document",
            "section": "required",
            "label": "Official ID document (passport or national ID card) - front and back sides",
            "required": True,
            "notes": "Make sure the image is straight and clearly readable.",
        },
        {
            "key": "cv",
            "section": "required",
            "label": "Curriculum Vitae (CV) - table format, up to date, and without gaps",
            "required": True,
        },
        {
            "key": "degree_certificates",
            "section": "required",
            "label": "Diploma(s) and degree certificate(s) - certified copy or original",
            "required": True,
        },
        {
            "key": "transcript",
            "section": "required",
            "label": "Diploma transcript / list of subjects and hours, if available",
            "required": False,
        },
        {
            "key": "license_registration",
            "section": "required",
            "label": "Professional license / registration from home country (if applicable to your profession)",
            "required": True,
        },
        {
            "key": "work_experience",
            "section": "required",
            "label": "Proof of relevant work experience (reference letters or employment certificates)",
            "required": True,
        },
        {
            "key": "language_b2_pflege",
            "section": "required",
            "label": "Proof of language level (B2 Pflege or equivalent)",
            "required": True,
            "notes": "If Fachsprachprüfung is required, please add the certificate when available.",
        },
        {
            "key": "good_standing",
            "section": "required",
            "label": "Certificate of Good Standing / Current Professional Standing (from competent authority)",
            "required": True,
        },
        {
            "key": "apostille_legalization",
            "section": "conditional",
            "label": "Apostille or legalization on foreign public documents, if required",
            "required": False,
            "notes": "Only for documents issued outside Germany when the authority requests it.",
            "conditional_on": ["requires_apostille"],
        },
        {
            "key": "name_change",
            "section": "conditional",
            "label": "Proof of name change (e.g. marriage certificate), if applicable",
            "required": False,
        },
        {
            "key": "translations",
            "section": "translations",
            "label": "Certified translations of all non-German documents",
            "required": True,
            "notes": "Must be prepared by publicly sworn translators.",
        },
        {
            "key": "contact",
            "section": "formal",
            "label": "Current contact information (address, email, phone)",
            "required": True,
        },
    ],
    # Helper texts for UI tooltips / FAQ
    "helptexts": {
        "quality": "Upload straight, clearly readable scans or photos. Include all pages.",
        "translations": "Translations must be certified by officially sworn translators.",
        "conditional": "Only upload items marked 'if applicable' when relevant to your case.",
        "apostille": "Apostilles/legalizations may be required for foreign public documents depending on the issuing country and the authority’s instructions.",
    },
    # Email templates (English, polite tone)
    "emails": {
        "missing_docs_subject": "Your recognition documents (Bavaria) - missing items",
        "missing_docs_body": (
            "Dear {name},\n\n"
            "Thank you for submitting your documents. After the initial review, "
            "the following items are still missing for your Bavaria submission:\n\n"
            "{missing_list}\n\n"
            "Please make sure your uploads are clearly readable and that any non-German "
            "documents are accompanied by certified translations. If apostilles/legalizations "
            "are required, please attach them as well.\n\n"
            "If you have any questions, we are happy to assist.\n"
            "Best regards,\n{signature}"
        ),
    },
    # Validation rules in line with BE/NW
    "rules": {
        "at_least_one_id": ["id_document"],
        "must_translate_if_not_de": [
            "degree_certificates",
            "transcript",
            "license_registration",
            "work_experience",
            "good_standing",
        ],
        "require_language_b2": ["language_b2_pflege"],
        "require_apostille_if_flag": {
            "flag": "requires_apostille",
            "keys": [
                "degree_certificates",
                "transcript",
                "license_registration",
                "good_standing",
            ],
        },
    },
}


# TODO: Add more states

# ---------------------------------------------------------------------------
# Fallback helpers: prefer STATE_RULES; otherwise use STATE_CHECKLISTS
# ---------------------------------------------------------------------------

from typing import Dict, List, Optional, Tuple

# Common aliases so callers can pass "Berlin", "BE", "NRW", etc.
# Not neccessary for ui because of dropdown, but useful for backend calls.
# TODO: Add more aliases as needed

STATE_ALIASES: Dict[str, str] = {
    # Berlin
    "BE": "BE", "Berlin": "BE",
    # Bavaria / Bayern (prepared for future expansion)
    "BY": "BY", "Bavaria": "BY", "Bayern": "BY",
    # North Rhine-Westphalia / NRW (prepared for future expansion)
    "NW": "NW", "NRW": "NW", "North Rhine-Westphalia": "NW", "Nordrhein-Westfalen": "NW",
}

def _normalize_state_to_code(state: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (state_code, state_label_guess).
    If the state is only in STATE_CHECKLISTS (no code), returns (None, label_from_input_or_match).
    """
    if not state:
        return None, None
    s = state.strip()
    # 1) Exact alias to code if we know it
    code = STATE_ALIASES.get(s)
    if code:
        return code, STATE_RULES.get(code, {}).get("state_label", s)
    # 2) Try direct code match
    if s in STATE_RULES:
        return s, STATE_RULES[s].get("state_label", s)
    # 3) Try label match inside STATE_RULES (case-insensitive)
    for code_key, cfg in STATE_RULES.items():
        if cfg.get("state_label", "").lower() == s.lower():
            return code_key, cfg.get("state_label")
    # 4) Fall back to checklist keys (exact or case-insensitive)
    if s in STATE_CHECKLISTS:
        return None, s
    for label in STATE_CHECKLISTS.keys():
        if label.lower() == s.lower():
            return None, label
    return None, None

def get_state_ruleset(state: str) -> Optional[dict]:
    """
    Return the full structured ruleset from STATE_RULES for a state (by code or label),
    or None if no structured ruleset exists.
    """
    code, _ = _normalize_state_to_code(state)
    return STATE_RULES.get(code) if code else None

def get_ui_payload(state: str, locale: str = "en-DE") -> dict:
    """
    Unified UI payload:
      - If a structured ruleset exists: returns sections with items.
      - Else: returns a single 'Checklist' section built from STATE_CHECKLISTS.

    Return shape:
    {
        "state_code": "BE" | None,
        "state_label": "Berlin" | "NRW" | ...,
        "sections": [
            {
                "key": "required" | "conditional" | ... | "checklist",
                "title": "Mandatory documents" | "Checklist",
                "items": [{"key": "...", "label": "...", "required": bool}]
            }, ...
        ],
        "emails": {...}  # if available in structured ruleset
    }
    """
    code, label_guess = _normalize_state_to_code(state)
    rules = STATE_RULES.get(code) if code else None

    if rules:
        # Build sections in configured order
        sections_cfg = rules.get("sections", [])
        by_section: Dict[str, List[dict]] = {s["key"]: [] for s in sections_cfg}
        for item in rules.get("checklist", []):
            by_section.setdefault(item["section"], []).append({
                "key": item.get("key"),
                "label": item.get("label"),
                "required": bool(item.get("required", False)),
            })
        # Preserve declared order of sections
        sections_out = []
        for s in sections_cfg:
            items = by_section.get(s["key"], [])
            sections_out.append({
                "key": s["key"],
                "title": s["title"],
                "items": items,
            })
        return {
            "state_code": rules.get("state_code"),
            "state_label": rules.get("state_label", label_guess or state),
            "sections": sections_out,
            "emails": rules.get("emails", {}),
        }

    # Fallback to simple list
    _, checklist_label = _normalize_state_to_code(state)
    simple_items = STATE_CHECKLISTS.get(checklist_label or state, [])
    return {
        "state_code": code,  # likely None in fallback
        "state_label": checklist_label or state,
        "sections": [{
            "key": "checklist",
            "title": "Checklist",
            "items": [
                {"key": f"item_{i+1}", "label": label, "required": True}
                for i, label in enumerate(simple_items)
            ],
        }],
        "emails": {},
    }

def get_flat_checklist(state: str) -> List[str]:
    """
    Convenience: return a flattened list of labels for quick displays or CSV exports.
    Prefers structured rules if present; else uses simple checklist.
    """
    payload = get_ui_payload(state)
    out: List[str] = []
    for section in payload.get("sections", []):
        for item in section.get("items", []):
            out.append(item.get("label", ""))
    return out

# --------------------------
# Example usage (keep as docs or remove in production):
# --------------------------
# >>> get_state_ruleset("Berlin")        # returns full dict for BE (structured)
# >>> get_ui_payload("BE")               # UI-ready data with sections/items
# >>> get_ui_payload("NRW")              # falls back to simple STATE_CHECKLISTS["NRW"]
# >>> get_flat_checklist("Bavaria")      # flat list of labels
