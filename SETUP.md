# HR Analysis — Environment Setup Guide
Team 4: Diversity & Inclusion Officers

---

## Prerequisites
- Python 3.9 or higher
- Git
- VS Code with Python + Jupyter extensions installed

---

## Step 1 — Clone the Repository
```bash
git clone <your-repo-url>
cd HR-Analysis
```

## Step 2 — Create Virtual Environment
```bash
python -m venv venv
```

## Step 3 — Activate Virtual Environment
```bash
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```
You should see (venv) at the start of your terminal prompt.

## Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 5 — Register Jupyter Kernel
```bash
python -m ipykernel install --user --name=hr-analysis --display-name "HR Analysis (venv)"
```

## Step 6 — Select Kernel in VS Code
1. Open any .ipynb file in VS Code
2. Click "Select Kernel" in the top right corner
3. Click "Python Environments"
4. Select "hr-analysis" or the venv folder

## Step 7 — Run the Streamlit App
```bash
cd src
streamlit run app.py
```
App will open automatically at http://localhost:8501

---

## Project Structure
```
HR-Analysis/
├── data/
│   ├── ACSEEO5Y2018.EEOALL1R-2026-02-16T043140.csv   ← raw Census data
│   └── clean_eeo_data.csv                             ← processed data
├── src/
│   ├── analysis.ipynb                                 ← data wrangling notebook
│   └── app.py                                         ← Streamlit app
├── requirements.txt                                   ← dependencies
├── SETUP.md                                           ← this file
└── .gitignore
```

---

## Troubleshooting

**venv not showing in VS Code kernel list:**
- Press Cmd+Shift+P → "Python: Select Interpreter" → "Enter interpreter path" → type ./venv/bin/python

**pyarrow build error:**
```bash
pip install streamlit --prefer-binary
```

**FileNotFoundError for CSV:**
- Make sure you are running the notebook from inside the src/ folder
- Use absolute path: /Users/yourname/Documents/.../HR-Analysis/data/filename.csv

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

---

## Data Source
US Census Bureau — American Community Survey
EEO (Equal Employment Opportunity) 5-Year Estimates, 2018
