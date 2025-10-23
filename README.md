# Brisbane Business Bridge AI

**Intelligent Networking for Smart Cities**

AI-powered delegate matching system for Brisbane City Council's international business events, including the Boldly Brisbane Forum and 2025 Asia Pacific Cities Summit (APCS).

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
NOTION_TOKEN=secret_...
NOTION_DATABASE_ID=...
```

### 3. Run the Application

```bash
python app.py
```

Open your browser to: **http://localhost:5000**

---

## Features

### Current (MVP - v1.0)

✅ **Upload CV/Capability Statement** (PDF or DOCX)
✅ **AI-Powered Matching** against 42 Brisbane delegates
✅ **Top 3 Recommendations** with match scores
✅ **Synergy Analysis** for each match
✅ **Contact Information** for follow-up

### Coming Soon

🔄 **Notion Integration** - Persistent storage of all matches
🔄 **Claude AI Integration** - Advanced synergy analysis
🔄 **PDF Report Generation** - Professional downloadable reports
🔄 **Email Notifications** - Auto-send results to Brisbane City Council
🔄 **Multi-language Support** - Arabic, Mandarin, Japanese
🔄 **APCS 2025 Scaling** - Support for 300+ delegates

---

## Architecture

```
Brisbane Business Bridge AI
│
├── Frontend (Web Interface)
│   └── templates/index.html
│
├── Backend (Flask API)
│   ├── app.py (main application)
│   ├── extract_delegates.py (PDF parsing)
│   └── data/delegates.json (knowledge base)
│
├── AI Matching Engine
│   ├── Text extraction (PyPDF2, python-docx)
│   ├── Semantic matching (sentence-transformers)
│   └── Scoring algorithm
│
└── Integrations (TODO)
    ├── Notion API (persistent CRM)
    ├── Claude AI (advanced analysis)
    └── Report Gen (PDF output)
```

---

## How It Works

1. **User uploads** CV or capability statement
2. **System extracts** text content from document
3. **AI analyzes** profile against 42 Brisbane delegates
4. **Matching algorithm** calculates compatibility scores based on:
   - Sector alignment (30%)
   - Interested sectors overlap (10-40%)
   - Objectives alignment (40%)
   - Business type compatibility (20%)
5. **Top 3 matches** returned with detailed synergy analysis
6. **Results stored** in Notion for Brisbane City Council tracking

---

## Delegates Knowledge Base

The system currently includes **42 delegates** from the 2025 City of Brisbane Business Mission Booklet:

- **8** Brisbane City Council officials
- **3** Brisbane Economic Development Agency executives
- **31** Business delegates across sectors:
  - Property Development (9)
  - Professional Services (12)
  - Food & Agribusiness (3)
  - Tourism & Hospitality (1)
  - Manufacturing (1)
  - Infrastructure & Transport (2)
  - Finance & Banking (1)
  - And more...

---

## API Endpoints

### POST `/upload`
Upload user profile and get top 3 delegate matches

**Request:**
- Form Data:
  - `name` (required): User's name
  - `company` (required): Company name
  - `email` (required): Email address
  - `industry` (optional): Industry/sector
  - `file` (required): PDF or DOCX file

**Response:**
```json
{
  "success": true,
  "user": {
    "name": "Luis Rico",
    "company": "Rico Engineering Services",
    "email": "luis@resgroup.ae"
  },
  "matches": [
    {
      "rank": 1,
      "name": "Nike Zhao",
      "company": "PEER Consulting Engineers",
      "score": 87,
      "synergy_analysis": "..."
    }
  ]
}
```

### GET `/api/delegates`
Get list of all delegates

### GET `/api/stats`
Get system statistics

---

## Integration with Your Existing Notion Code

### Step 1: Add Your Notion Integration

In `app.py`, find the TODO comment:

```python
# TODO: Store in Notion (use your existing Notion integration code here)
# notion_crm.store_match(user_info, matches)
```

Replace with your working Notion code. The data structure is:

```python
user_info = {
    'name': str,
    'company': str,
    'email': str,
    'industry': str
}

matches = [
    {
        'delegate': {...},  # Full delegate object
        'score': int,       # 0-100
        'synergy_analysis': str
    }
]
```

### Step 2: Example Integration

```python
from notion_client import Client

notion = Client(auth=os.getenv('NOTION_TOKEN'))

def store_in_notion(user_info, matches):
    for match in matches:
        notion.pages.create(
            parent={"database_id": os.getenv('NOTION_DATABASE_ID')},
            properties={
                "Name": {
                    "title": [{
                        "text": {
                            "content": f"{user_info['name']} ↔ {match['delegate']['name']}"
                        }
                    }]
                },
                "User Company": {
                    "rich_text": [{"text": {"content": user_info['company']}}]
                },
                "Delegate": {
                    "rich_text": [{"text": {"content": match['delegate']['name']}}]
                },
                "Match Score": {
                    "number": match['score']
                },
                "Event": {
                    "select": {"name": "Boldly Brisbane Forum 2025"}
                }
            }
        )
```

---

## Upgrading to Claude AI

To enable advanced synergy analysis, update the `generate_synergy_analysis_simple()` function:

```python
import anthropic

def generate_synergy_analysis_ai(user_text, delegate):
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    prompt = f"""You are an expert business matchmaker for Brisbane City Council.

USER PROFILE:
{user_text[:1000]}

DELEGATE PROFILE:
Name: {delegate['name']}
Company: {delegate['company']}
Objectives: {delegate['objectives']}

Analyze synergies and provide:
1. Top 3 alignment areas
2. Collaboration opportunities
3. Meeting talking points
4. Potential challenges

Keep under 300 words."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
```

---

## Deployment Options

### Option 1: Local Demo (Today)

```bash
python app.py
# Access at http://localhost:5000
```

### Option 2: Cloud Deployment (Vercel/Heroku)

**Vercel:**
```bash
vercel deploy
```

**Heroku:**
```bash
git init
heroku create brisbane-bridge-ai
git push heroku main
```

### Option 3: Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

---

## Testing

### Test with Sample Data

```bash
# Use the example CV from your RES microsite
curl -X POST http://localhost:5000/upload \
  -F "name=Luis Rico" \
  -F "company=Rico Engineering Services" \
  -F "email=luis@resgroup.ae" \
  -F "industry=AI Technology" \
  -F "file=@sample_cv.pdf"
```

---

## Future Enhancements

### Phase 2 (APCS 2025 - Oct 27-29)
- Scale to 300+ delegates
- Real-time matching during event
- Mobile app (iOS/Android)
- QR code check-in integration
- Meeting scheduler
- Live chat translation

### Phase 3 (Platform - 2026)
- White-label for other cities
- CRM integrations (HubSpot, Salesforce, Qodequay)
- Analytics dashboard
- API marketplace
- Multi-tenant architecture

---

## Support

**For Brisbane City Council:**
Contact: InternationalRelations@brisbane.qld.gov.au

**For Technical Issues:**
Luis Rico - luis@resgroup.ae
Rico Engineering Services RES FZ-LLC

---

## License

Copyright © 2025 Rico Engineering Services RES FZ-LLC
All Rights Reserved.

Built for Brisbane City Council's Boldly Brisbane Forum & APCS 2025.

---

**Brisbane Business Bridge AI** - *Connecting Cities, Empowering Business*
