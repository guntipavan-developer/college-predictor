# EAMCET College Predictor — Technology Stack

> AI-Powered Engineering College Admission Predictor for AP & TS
> Built with a rule-based cutoff filter backed by official EAMCET counselling data.

---

## Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.14 | Core programming language |
| **FastAPI** | 0.128.0 | REST API framework — handles `/predict`, `/stats`, `/` routes |
| **Uvicorn** | 0.40.0 | ASGI server — runs the FastAPI app on port 8000 |
| **Pandas** | 3.0.1 | Data loading, cleaning, and filtering from `data.csv` |
| **NumPy** | (via Pandas) | Numeric coercion and array operations |

### Running the Server
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Machine Learning (Training Only)

> Used in `train_model.py` — the trained model is saved but **not used** in live predictions.

| Library / Algorithm | Role |
|---|---|
| **scikit-learn** | ML training framework |
| `RandomForestClassifier` | Ensemble of 100 decision trees — predicts college from rank + branch |
| `LabelEncoder` | Encodes college names and branch codes into integers |
| **joblib** | Serialises and saves trained models to `.pkl` files |

### Model Files Generated
| File | Size | Contents |
|---|---|---|
| `model.pkl` | ~387 MB | Trained RandomForest model |
| `le_college.pkl` | ~11 KB | LabelEncoder for college names (274 classes) |
| `le_branch.pkl` | ~856 B | LabelEncoder for branch codes (64 classes) |

---

## Frontend

| Technology | Purpose |
|---|---|
| **HTML5** | Page structure and semantic markup |
| **CSS3** | Styling — gradients, animations, responsive layout |
| **Vanilla JavaScript (ES6+)** | `fetch()` API calls, DOM manipulation, form validation |
| **Google Fonts — Inter** | Clean, modern typography |

### Key UI Features
- Light lavender gradient background
- Centered white card layout
- Blue → purple gradient "Get Predictions" button
- Results table with match-strength progress bars
- Responsive 3-column dropdown row (Gender / Category / Branch)

---

## Data

| File | Format | Size | Description |
|---|---|---|---|
| `data.csv` | CSV | 323 KB | Official EAMCET cutoff ranks — 1,514 rows × 31 columns |

### Dataset Columns (key ones)
| Column | Description |
|---|---|
| `NAMEOFTHEINSTITUTION` | College full name |
| `branch_code` | Branch code (CSE, ECE, EEE, etc.) |
| `OC_BOYS / OC_GIRLS` | Open Category closing ranks |
| `SC_BOYS / SC_GIRLS` | Scheduled Caste closing ranks |
| `ST_BOYS / ST_GIRLS` | Scheduled Tribe closing ranks |
| `BCA_BOYS` → `BCE_GIRLS` | BC-A through BC-E closing ranks |

---

## System Architecture

```
┌─────────────────────────────────────┐
│        Browser (Client)             │
│   HTML  +  CSS  +  JavaScript       │
└────────────────┬────────────────────┘
                 │  HTTP GET /predict?rank=&branch=&category=&gender=
                 ▼
┌─────────────────────────────────────┐
│       FastAPI  (main.py)            │
│       Served via Uvicorn            │
│       http://localhost:8000         │
└────────────────┬────────────────────┘
                 │  pd.read_csv("data.csv")
                 ▼
┌─────────────────────────────────────┐
│       Pandas DataFrame              │
│  Filter: cutoff_rank >= input_rank  │
│  Sort by closest cutoff             │
│  Return top 10 colleges             │
└─────────────────────────────────────┘
```

---

## Prediction Logic (Core Algorithm)

```python
# main.py — what runs on every /predict request
col = f"{category}_{gender}"            # e.g. "OC_BOYS"

df[col] = pd.to_numeric(df[col], errors='coerce')
df = df[df['branch'].str.upper() == branch]

possible = df[df[col] >= rank]          # colleges where cutoff >= your rank
possible = possible.sort_values(col)    # sort by closest match

result = possible.head(10)              # top 10 results
```

> **Note:** This is a direct rule-based data lookup — not a machine learning prediction.
> The approach is deterministic, transparent, and 100% based on official cutoff data.

---

## ML Model Comparison Results

| Algorithm | Train Acc | Test Acc | Status |
|---|---|---|---|
| Random Forest (100 trees) | 96.58% | 1.40% | Trained, not used in API |
| Decision Tree | 96.58% | 1.05% | Trained, not used in API |
| **Direct Cutoff Filter** | **96.40%** | **1.75%** | **LIVE in production** |
| Decision Stump | 37.11% | 1.75% | Experimental |
| Naive Bayes (Gaussian) | 8.07% | 2.10% | Experimental |
| Linear Regression (OLS) | 0.44% | 1.05% | Experimental |
| KNN (k=5) | 21.84% | 0.70% | Experimental |

> Low test accuracy is expected — this is a 274-class classification problem.
> The direct filter returns **all eligible colleges**, not just one predicted college, making it more useful for students.

---

## Project Structure

```
eamcet_pred/
│
├── main.py              # FastAPI app — API routes + prediction logic
├── train_model.py       # ML training script (RandomForest)
├── evaluate_models.py   # Algorithm comparison and accuracy report
├── index.html           # Frontend UI (served by FastAPI)
├── data.csv             # Official EAMCET cutoff dataset
├── model.pkl            # Trained RandomForest (saved, not used in API)
├── le_college.pkl       # LabelEncoder — college names
├── le_branch.pkl        # LabelEncoder — branch codes
├── TECHNOLOGIES.md      # This file
└── __pycache__/         # Python bytecode cache
```

---

## API Endpoints

| Method | Route | Parameters | Description |
|---|---|---|---|
| `GET` | `/` | — | Serves `index.html` frontend |
| `GET` | `/predict` | `rank`, `branch`, `category`, `gender` | Returns matching colleges |
| `GET` | `/stats` | — | Returns total colleges, branches, rows |

### Example Request
```
GET /predict?rank=15000&branch=CSE&category=OC&gender=BOYS
```

### Example Response
```json
{
  "input_rank": 15000,
  "branch": "CSE",
  "category": "OC",
  "gender": "BOYS",
  "colleges": [
    { "college": "PRASAD V POTLURI SIDDHARTHA INSTT OF TECHNOLOGY", "OC_BOYS": 15207 },
    { "college": "MOHAN BABU UNIVERSITY", "OC_BOYS": 15759 }
  ]
}
```

---

*Data sourced from official AP & TS EAMCET counselling records. Results are indicative — always verify with official portals.*
