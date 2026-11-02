# Hospital Portal - Incoming Ambulance APIs

Backend module for the Hospital Portal. All data is synthetic.

## Setup
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

## Load test data
    python -m app.seed

## Run
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to try the APIs (use header `x-hospital-id`: 1 or 2).

## Test
    python -m pytest -q

## Docs
See `docs/api_contract.md` for endpoints, examples, field mapping and assumptions.