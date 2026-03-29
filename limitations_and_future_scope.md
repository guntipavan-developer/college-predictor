# System Limitations & Future Scope

While the EAMCET College Predictor is currently highly optimized, accurate, and blazing fast (~18ms), there are several constraints in its present architecture and data model. Addressing these limitations outlines a strong roadmap for future development.

---

## 🛑 Current Limitations

### 1. Static Single-Year Dataset
* **The Constraint:** The application relies entirely on a single static `data.csv` file representing one year of counselling closing ranks. 
* **The Impact:** It does not account for year-over-year fluctuations in seat availability, paper difficulty, or changes in student branch preferences. If a new college is added or closed next year, it won't reflect unless the CSV is manually updated.

### 2. Lack of "Local vs. Non-Local" Region Filtering
* **The Constraint:** In AP and TS EAMCET, seats are heavily divided by university boundaries (e.g., Andhra University (AU), Sri Venkateswara University (SVU), Osmania University (OU), and Unreserved/Non-Local).
* **The Impact:** The current predictor assumes the student is eligible for the general cutoff rank listed, which might lead to inaccurate predictions if a seat is reserved exclusively for a local district candidate.

### 3. Missing Qualitative College Data
* **The Constraint:** The result table only outputs the College Name and the Cutoff Rank. 
* **The Impact:** Students choosing a college usually care about Placements, NAAC/NBA Accreditation, fee structures, and campus location. This context is absent, forcing the student to Google each result manually.

### 4. Memory-Bound Architecture (In-Memory Scaling Limits)
* **The Constraint:** Loading `data.csv` into a Pandas DataFrame in RAM makes the app incredibly fast because the dataset is tiny (~323 KB). 
* **The Impact:** If the project were expanded to include 10 years of historic data across *all* national entrance exams (JEE, NEET, MH-CET, KCET), the in-memory Pandas dataframe could balloon to several gigabytes, requiring an infrastructural shift to a caching layer like **Redis** or a fast database like **PostgreSQL + pgBouncer**.

### 5. Deterministic Rigidity
* **The Constraint:** Because it uses a strict mathematical filter (`cutoff >= rank`), if a student's rank is `15,005` and a college cutoff was `15,000`, the system will outright reject the college. 
* **The Impact:** In reality, cutoffs flex by hundreds of ranks every year. A pure deterministic filter misses "borderline" or "highly probable" colleges that an ML-based probability model would have flagged.

---

## 🚀 Future Scope & Upgrades

### 1. Multi-Year Trend Analysis & Predictive ML
*   **Enhancement:** Instead of a single cut-off number, aggregate 3 to 5 years of historical counselling data. 
*   **Implementation:** Train a Time-Series forecasting model (like ARIMA or Prophet) to predict *next year's* expected cut-off range, providing the student with a "Safe", "Moderate", or "Risky" gauge for each college.

### 2. Comprehensive Filter Engine
*   **Enhancement:** Add detailed input toggles to the UI.
*   **Implementation:** 
    *   **Region:** Toggles for AU, SVU, OU, or Non-Local.
    *   **Minority Status:** Muslim/Christian minority reservations.
    *   **Institutional Filters:** Let users filter by "Max Fee: ₹1 Lakh", "Co-Ed vs Women-Only", or "Govt vs Private".

### 3. Chatbot Integration (WhatsApp / Telegram)
*   **Enhancement:** Meet the students where they are.
*   **Implementation:** Because the FastAPI backend is already built as a clean REST API (`/predict`), it is trivial to connect it to the Twilio API or Telegram Bot API. A student could simply message a bot: *"Rank 15000 CSE OC Boys"* and receive an instant top-5 college list back via WhatsApp.

### 4. Detailed College Profiles & Scraping
*   **Enhancement:** Convert the predicted college rows into clickable links.
*   **Implementation:** Build a scraping pipeline or connect to an educational API to open a modal window displaying the college's Address, Average Package (LPA), official website, and campus images when a result is clicked.

### 5. Progressive Web App (PWA) Conversion
*   **Enhancement:** Make the predictor mobile-native without needing an App Store.
*   **Implementation:** Add a `manifest.json` and a Service Worker to the frontend so students can "Install" the page to their Android/iOS home screens. Once the initial dataset is cached locally in the browser, predictions could run entirely offline natively on the phone.

### 6. Mock Options Entry (Counselling Simulator)
*   **Enhancement:** Help students prepare for the official web-options entry phase.
*   **Implementation:** Allow users to "Add to Cart" or "Shortlist" predicted colleges, rearrange them in priority order, and export a formatted PDF list ready to be referenced on the day of official government counselling.
