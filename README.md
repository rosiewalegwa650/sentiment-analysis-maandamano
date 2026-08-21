# 🇰🇪 Maandamano Pulse: Kenyan Civic Sentiment & Tension Monitoring System

**Maandamano Pulse** is a civic technology platform designed to collect, analyze, and monitor public social media discussions surrounding protests (*maandamano*), economic policy (e.g., Finance Bill), and civic demonstrations across Kenya.

The platform uses multilingual transformer models (**XLM-RoBERTa**) combined with specialized rule-based lexicons for **Swahili** and **Sheng** (Kenyan urban code-switching dialect) to provide real-time sentiment analysis, spatial location mapping, and escalation safety scores.

---

## ✨ Features & Kenyan Cultural Customizations

- **🇰🇪 Authentic Kenyan Identity & UI Design**:
  - Kenyan flag shield badge & Maasai-inspired cultural header accents.
  - Kenyan urban hotspots monitoring (Nairobi CBD, Kibra, Mathare, Kondele, Eldoret, Githurai, Mombasa, etc.).
  - Language classification & badges for **Sheng**, **Swahili**, and **English**.
- **🧠 Multilingual Sentiment Engine**:
  - Contextual embeddings via XLM-RoBERTa (`cardiffnlp/twitter-xlm-roberta-base-sentiment`).
  - Specialized Sheng lexicon alignment (detecting expressions like *noma*, *wantam*, *ngori*, *poa*, *fiti*, *zakayo*, *mbogi*).
- **🚨 Escalation & Tension Signal Score**:
  - Calculates a 0–100 risk score based on negative sentiment density, high-risk keywords (*teargas*, *arrests*, *violence*, *risasi*), and posting volume velocity across 24h/48h comparative windows.
- **📡 Multi-Source Ingestion Pipeline**:
  - Synthetic Kenyan Social Feed Generator (zero-credential demo mode).
  - Live Reddit Collector (`praw` integration for subreddits like `r/Kenya`).
  - Live X / Twitter API v2 Search Collector.

---

## 📁 Repository Structure

```
.
├── backend/
│   ├── data_collection/
│   │   ├── mock_generator.py      # Synthetic Kenyan social stream generator
│   │   ├── reddit_collector.py    # PRAW Reddit search integration
│   │   └── twitter_collector.py   # X (Twitter) API v2 collector
│   ├── nlp/
│   │   ├── escalation.py          # Escalation risk score algorithm
│   │   ├── language_detection.py  # Sheng, Swahili, English detector
│   │   ├── preprocessing.py       # Cleaning, tokenization & deduplication
│   │   └── sentiment_model.py     # XLM-RoBERTa + Sheng lexicon classifier
│   ├── routes/
│   │   ├── collect.py             # POST /api/collect pipeline route
│   │   └── dashboard.py           # GET /api/dashboard/* analytics routes
│   ├── tests/
│   │   └── test_backend.py        # Pytest backend test suite
│   ├── app.py                     # Flask entry point
│   ├── config.py                  # Environment config & keywords
│   ├── database.py                # SQLAlchemy DB instance
│   ├── models.py                  # DB models (SocialMediaPost, SentimentResult, EscalationAlert)
│   └── requirements.txt           # Backend Python dependencies
├── frontend/
│   ├── public/                    # Static React public assets
│   ├── src/
│   │   ├── App.js                 # React Dashboard application component
│   │   ├── App.css                # Custom Kenyan dashboard styling
│   │   ├── App.test.js            # Frontend Jest test suite
│   │   └── index.js               # React DOM entry point
│   └── package.json               # Frontend dependencies & scripts
├── .env.example                   # Sample environment variable template
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher

---

### Backend Setup (Flask API)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables** *(Optional for API Keys)*:
   Copy `.env.example` to `.env` in the root or backend directory:
   ```bash
   cp .env.example .env
   ```

4. **Run Backend Unit Tests**:
   ```bash
   python3 -m pytest backend/tests/test_backend.py
   ```

5. **Start the Flask Backend Server**:
   ```bash
   python3 -m backend.app
   # Or from within backend directory: python3 app.py
   ```
   *The Flask API will run at `http://localhost:5000/`.*

---

### Frontend Setup (React App)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Run Frontend Tests**:
   ```bash
   npm test -- --watchAll=false
   ```

4. **Start the React Development Server**:
   ```bash
   npm start
   ```
   *The React UI will open at `http://localhost:3000/`.*

---

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Health check endpoint returning `{"status": "ok"}` |
| `/api/collect` | `POST` | Ingests data from source (`mock`, `reddit`, or `twitter`) and runs NLP pipeline |
| `/api/dashboard/summary` | `GET` | Overall sentiment metrics (positive, neutral, negative %) |
| `/api/dashboard/trends` | `GET` | Daily sentiment breakdown over time |
| `/api/dashboard/geographic` | `GET` | Location sentiment ranking (Kenyan hotspots) |
| `/api/dashboard/escalation`| `GET` | Current escalation risk score & alert level |
| `/api/dashboard/keywords`  | `GET` | Most frequent discussion keywords |
| `/api/posts` | `GET` | Live feed of stored posts with sentiment classifications |
| `/api/posts` | `DELETE` | Clears all collected post records |

---

## 🛡️ License & Attributions

Developed for civic technology and social impact monitoring in Kenya.
