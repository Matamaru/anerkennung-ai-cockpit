# S3 Model Roadmap (Heroku)

This roadmap describes how to host LayoutLM models in S3 and use them on Heroku.

## Phase 1 — Storage + credentials
- Create an S3 bucket (e.g. `anerkennung-models`).
- Upload model dirs (start with passport token model):
  - `s3://anerkennung-models/models/passport/passport_layoutlmv3-token/`
- Create IAM user with read-only S3 access.
- Store credentials in Heroku config:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`
  - `CAESAR_S3_MODEL_PREFIX=s3://anerkennung-models/models/passport/`

## Phase 2 — Download script
- Add `scripts/fetch_models.py`:
  - Downloads a model directory from S3 to `/app/models/passport_layoutlmv3-token`
  - Skips download if already present
  - Validates required files exist

## Phase 3 — Boot integration
- Add a Heroku release/boot hook:
  - Option A: Procfile release process
    - `release: python scripts/fetch_models.py`
  - Option B: `HEROKU_POSTBUILD` hook
- Ensure download happens before web dyno starts.

## Phase 4 — Wiring to OCR
- Set:
  - `CAESAR_LAYOUTLM_TOKEN_MODEL_DIR=/app/models/passport_layoutlmv3-token`
  - `CAESAR_PASSPORT_LABEL_MAP_PATH=/app/backend/utils/label_maps/passport.json`
- Keep fallback OCR if model is missing.

## Phase 5 — Monitor + cache
- Add logs: “model download started/finished”.
- Optional: versioning (e.g., `.../passport/v1/`).
- Optional: checksum validation.

## Phase 6 — Expand
- Repeat for diploma model once passport is stable.
- Add optional per-domain env vars (passport/diploma).
