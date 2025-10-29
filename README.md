# Anerkennung AI Cockpit

## Problem Statement
TERN’s Germany pipeline is slowed by the Anerkennung (professional-recognition) process. Each federal state has different document requirements and communication formats. Many nurse applications are delayed or rejected because documents are incomplete, translated incorrectly, or sent to the wrong authority. This wastes recruiter time, frustrates candidates, and extends onboarding by months.

## Proposed Solution – “Anerkennung AI Cockpit”
A lightweight web platform that acts as a digital co-pilot for recognition workflows.

### Smart Checklist Engine

Uses AI to auto-detect the correct state authority based on address or employer.
Generates a dynamic, state-specific checklist (e.g., Berlin vs. Bavaria).

### Document Intelligence

- OCR + LLM pipeline scans uploaded PDFs/JPEGs, extracts key fields (name, license no., stamps).
- Validates completeness and flags missing or inconsistent items.
- Suggests required certified translations and formats.

### Workflow & Communication Hub

- Pre-fills official request emails in German.
- Tracks recognition status per candidate; alerts recruiters to SLA risks.

### Insights Dashboard

- Displays “time-to-decision” metrics and predicted completion dates.
- Aggregates recurring issues to improve upstream document collection.

### Tech Stack (prototype)

- Python / FastAPI backend
- Tesseract + LangChain / OpenAI API for document parsing
- PostgreSQL for candidate-state mapping
- Flask frontend with lightweight auth (TERN SSO possible)

### Expected Impact & 10× Potential

- Metric	Current	Target (90 days MVP)	10× Scale Potential
- File rejection rate	≈ 35 %	< 10 %	Automated validation for all countries
- Avg. recognition time	3 months	≤ 1 months	AI co-pilot across EU/UK recognitions
- Recruiter hours per case	~10 h	< 2 h	24/7 self-service portal for candidates

## Preparations

### Create virtual environment

```
python3 -m venv .venv
```

### Activate virtual environment (POSIX)

```
source .venv/bin/activate
```
(For Windows OS use appropriate procedure)

### Install required libraries

```
pip install -r requirements.txt
```

## OCR requirements

```
sudo apt update 
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu tesseract-ocr-osd
```