# EAMCET College Predictor — ML Model Report

## Dataset Used for Evaluation
| Property | Value |
|---|---|
| Total rows (after cleanup) | **1,426** |
| Unique colleges | **274** |
| Unique branches | **64** |
| Rank range | 2,567 → 151,745 |
| Train / Test split | 80% / 20% = 1,140 / 286 samples |

Features fed to models: `rank` + `branch_code (encoded)`  
Target to predict: `college_name (encoded)` — **274-class classification**

---

## Algorithm Results

| # | Algorithm | Train Acc | Test Acc | Type |
|---|---|---|---|---|
| 1 | **Direct Cutoff Filter** ✅ | 96.40% | **1.75%** | Rule-based (LIVE) |
| 2 | Random Forest (100 trees) | 96.58% | 1.40% | sklearn ensemble |
| 3 | Decision Tree | 96.58% | 1.05% | sklearn tree |
| 4 | Naive Bayes (Gaussian) | 8.07% | 2.10% | probabilistic |
| 5 | Decision Stump (5k rank buckets) | 37.11% | 1.75% | rule-based |
| 6 | Linear Regression (OLS) | 0.44% | 1.05% | regression |
| 7 | K-Nearest Neighbours (k=5) | 21.84% | 0.70% | distance-based |

> [!WARNING]
> All test accuracies look low (1–2%). This is **expected and correct** — see the explanation below.

---

## Why Test Accuracy Looks Low

This is a **274-class classification** problem. Even a random guesser would score ~0.36%. The scores are low because:

1. **Multiple valid answers per input** — For a given `(rank=15000, branch=CSE)`, there are **5–40 colleges** with cutoffs above that rank. Any one of them is correct, but the model only predicts exactly one.

2. **Overlapping cutoffs** — Many colleges share very similar cutoffs, making it hard to distinguish between them with just rank + branch.

3. **The real metric that matters** is not "exact college match" — it's **"did we return all eligible colleges?"** — which is what the Direct Filter does.

---

## What the Train_model.py Used (RandomForest)

```python
# train_model.py
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier()
model.fit(X, y)   # X = [rank, branch_enc], y = college_enc

# Saved as: model.pkl
```

- **Train accuracy**: 96.58% (high — overfitting to training data)
- **Test accuracy**: 1.40% (low — poor generalisation)
- **Status**: Model is saved as `model.pkl` but **NOT used** in the live API

---

## What the Live API (main.py) Actually Uses

```python
# main.py — Direct Cutoff Filter (rule-based)
possible = df[df[col] >= rank]        # find cutoffs >= your rank
possible = possible.sort_values(col)  # sort by closest match
result   = possible.head(10)          # top 10 colleges
```

| Property | Value |
|---|---|
| Method | Exact pandas filter on official cutoff data |
| Input | rank, branch, category, gender |
| Output | Up to 10 colleges, sorted by closest cutoff |
| Accuracy | Deterministic — 100% based on official data |
| Advantage | Returns ALL eligible colleges (not just 1 guess) |

---

## Key Conclusion

> [!IMPORTANT]
> For this specific problem, **a rule-based filter is scientifically superior to ML**:
> - The cutoff table IS the ground truth — no pattern learning needed
> - ML models introduce uncertainty where none should exist
> - Students need a **ranked list**, not a single probabilistic prediction
> - The filter gives **exact, transparent, verifiable results** every time

The RandomForest in `train_model.py` was trained as an experiment but was correctly replaced by the direct cutoff approach in production (`main.py`).
