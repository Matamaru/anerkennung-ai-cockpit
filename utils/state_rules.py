#****************************************************************************
#    Application:   Annerkennung Ai Cockpit
#    Module:        utils.state_rules         
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

# Simple, editable checklists per Bundesland for nurse recognition (Anerkennung) MVP.
# NOTE: This is a starter set for prototyping. Replace/expand with verified, up-to-date rules.

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
