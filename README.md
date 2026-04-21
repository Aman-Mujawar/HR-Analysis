# Diverse STEM Talent Finder
**Team 4 — Diversity & Inclusion Officers | HR Consultants for Tech Consortium**

A Streamlit dashboard for identifying underutilized diverse STEM professionals across US states to support satellite office placement decisions.

---

## App Deployment URL
🔗 [Live App](https://hr-analysis-qddsys3bgzyl6xwtum2zkz.streamlit.app/)

> Replace this link after deploying on Streamlit Cloud (instructions below)

---

## Tech Stack
- Python 3.11
- Streamlit
- Plotly
- Pandas
- Groq API (LLaMA 3.3 — free tier)
- Data: US Census ACS EEO 2018 5-Year Estimates

---

## Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
Create the file `src/.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_..."
```
Get a free key at https://console.groq.com

### 5. Run the app
```bash
cd src
streamlit run app_1.py
```
Visit http://localhost:8501

---

## Project Structure