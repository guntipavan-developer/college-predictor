from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
DATA_FILE = os.path.join(BASE_DIR, "data.csv")

app = FastAPI(title="EAMCET College Predictor")

# ── CORS (allow all for local dev) ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load & clean dataset once at startup ────────────────────
data = pd.read_csv(DATA_FILE)
data.columns = data.columns.str.replace('\n', '').str.replace(' ', '')
data = data.rename(columns={
    'NAMEOFTHEINSTITUTION': 'college',
    'branch_code': 'branch',
    'AFFL.': 'affl'
})

# Filter out header rows that got mixed into data
data = data[data['affl'] != 'AFFL.']

# ── Category → column prefix mapping ────────────────────────
CATEGORY_MAP = {
    "OC":  "OC",
    "SC":  "SC",
    "ST":  "ST",
    "BCA": "BCA",
    "BCB": "BCB",
    "BCC": "BCC",
    "BCD": "BCD",
    "BCE": "BCE",
}

# ── Root endpoint (serves the HTML UI) ─────────────────────
@app.get("/")
def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"), media_type="text/html")


# ── Stats endpoint ───────────────────────────────────────────
@app.get("/stats")
def stats():
    valid_affl = [a for a in data['affl'].dropna().unique() if a.strip()]
    return {
        "colleges": int(data['college'].nunique()),
        "branches": int(data['branch'].nunique()),
        "total_rows": len(data),
        "affiliations": sorted(valid_affl)
    }


# ── Main prediction endpoint ─────────────────────────────────
@app.get("/predict")
def predict(rank: int, branch: str, category: str, gender: str = "BOYS", affl: str = "ALL"):

    branch   = branch.strip().upper()
    category = category.strip().upper()
    gender   = gender.strip().upper()
    affl_val = affl.strip().upper()

    if category not in CATEGORY_MAP:
        return {"error": f"Invalid category '{category}'. Valid: {list(CATEGORY_MAP.keys())}"}

    if gender not in ("BOYS", "GIRLS"):
        return {"error": "gender must be BOYS or GIRLS"}

    col = f"{CATEGORY_MAP[category]}_{gender}"          # e.g. "OC_BOYS"

    if col not in data.columns:
        return {"error": f"Column '{col}' not found in dataset."}

    # Work on a copy – convert cutoff column to numeric
    df = data[['college', 'branch', 'affl', col]].copy()
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=[col])

    # Filter by branch
    df = df[df['branch'].str.upper() == branch]

    # Filter by affiliation (if specific)
    if affl_val != "ALL":
        df = df[df['affl'].str.upper() == affl_val]

    if df.empty:
        return {
            "input_rank": rank,
            "branch": branch,
            "category": category,
            "gender": gender,
            "colleges": [],
        }

    # ── Core logic: colleges whose cutoff rank >= your rank ──
    possible = df[df[col] >= rank].sort_values(by=col)

    result = possible.head(10)

    return {
        "input_rank": rank,
        "branch": branch,
        "category": category,
        "gender": gender,
        "colleges": result[['college', col]].to_dict(orient='records'),
    }