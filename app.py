"""
Brisbane Business Bridge AI - Main Flask Application
AI-powered delegate matching for Brisbane City Council events
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
import docx
from dotenv import load_dotenv
import google.generativeai as genai
from notion_client import Client
from pdf_generator import generate_match_report_pdf

# Load environment variables
load_dotenv()

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
    print("[OK] Google Gemini API configured")
else:
    gemini_model = None
    print("[WARNING] Google API key not found - using simple analysis")

# Configure Notion
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
if NOTION_TOKEN and NOTION_DATABASE_ID:
    notion = Client(auth=NOTION_TOKEN)
    print("[OK] Notion integration configured")
else:
    notion = None
    print("[WARNING] Notion credentials not found - matches won't be saved")

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load delegates data
DELEGATES_PATH = Path(__file__).parent / "data" / "delegates.json"
with open(DELEGATES_PATH, 'r', encoding='utf-8') as f:
    DELEGATES = json.load(f)

print(f"[LOADED] {len(DELEGATES)} Brisbane delegates from knowledge base")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_text_from_pdf(file_path):
    """Extract text content from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
    return text


def extract_text_from_docx(file_path):
    """Extract text content from DOCX file"""
    text = ""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"[ERROR] DOCX extraction failed: {e}")
    return text


def simple_text_matching(user_text, delegate):
    """
    Simple keyword-based matching algorithm
    In production, this would use sentence transformers and embeddings
    """
    score = 0
    user_text_lower = user_text.lower()

    # Check sector alignment
    if delegate['sector'].lower() in user_text_lower:
        score += 30

    # Check interested sectors
    for sector in delegate['interested_sectors']:
        if sector.lower() in user_text_lower:
            score += 10

    # Check objectives alignment
    objectives_keywords = delegate['objectives'].lower().split()
    matching_keywords = sum(1 for keyword in objectives_keywords if keyword in user_text_lower and len(keyword) > 4)
    score += min(matching_keywords * 5, 40)

    # Business type bonus
    business_types = {
        'investor': ['invest', 'capital', 'fund', 'equity'],
        'funding seeker': ['seeking', 'funding', 'investment', 'capital'],
        'service provider': ['service', 'consulting', 'consulting', 'advisory'],
        'exporter': ['export', 'international', 'overseas']
    }

    if delegate['business_type'].lower() in business_types:
        keywords = business_types[delegate['business_type'].lower()]
        if any(kw in user_text_lower for kw in keywords):
            score += 20

    return min(score, 100)  # Cap at 100%


def match_delegates(user_profile_text, user_info):
    """
    Match user profile against all delegates and return top 3
    """
    print(f"[MATCHING] Analyzing profile for: {user_info.get('name', 'Unknown')}")

    # Calculate scores for all delegates
    matches = []
    for delegate in DELEGATES:
        score = simple_text_matching(user_profile_text, delegate)
        matches.append({
            'delegate': delegate,
            'score': score
        })

    # Sort by score (descending) and get top 3
    matches.sort(key=lambda x: x['score'], reverse=True)
    top_3 = matches[:3]

    print(f"[RESULTS] Top 3 matches found:")
    for i, match in enumerate(top_3, 1):
        print(f"  {i}. {match['delegate']['name']} ({match['delegate']['company']}) - {match['score']}%")

    return top_3


def store_match_in_notion(user_info, match, rank):
    """
    Store a match in Notion database
    """
    if not notion or not NOTION_DATABASE_ID:
        return False

    try:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {
                    "title": [{
                        "text": {
                            "content": f"{user_info['name']} ↔ {match['delegate']['name']}"
                        }
                    }]
                },
                "User": {
                    "rich_text": [{
                        "text": {"content": user_info['name']}
                    }]
                },
                "User Company": {
                    "rich_text": [{
                        "text": {"content": user_info['company']}
                    }]
                },
                "User Email": {
                    "email": user_info['email']
                },
                "Delegate": {
                    "rich_text": [{
                        "text": {"content": match['delegate']['name']}
                    }]
                },
                "Delegate Company": {
                    "rich_text": [{
                        "text": {"content": match['delegate']['company']}
                    }]
                },
                "Delegate Email": {
                    "email": match['delegate']['email']
                },
                "Match Score": {
                    "number": match['score']
                },
                "Rank": {
                    "number": rank
                },
                "Sector": {
                    "select": {"name": match['delegate']['sector']}
                },
                "Event": {
                    "select": {"name": "Boldly Brisbane Forum 2025"}
                },
                "Status": {
                    "select": {"name": "New Match"}
                }
            }
        )
        return True
    except Exception as e:
        print(f"[ERROR] Notion storage failed: {e}")
        return False


def generate_synergy_analysis_simple(user_text, delegate):
    """
    Generate synergy analysis using Google Gemini AI
    Falls back to simple analysis if API unavailable
    """
    if gemini_model:
        try:
            prompt = f"""You are an expert business matchmaker for Brisbane City Council's international networking events.

USER PROFILE (First 800 chars):
{user_text[:800]}

DELEGATE PROFILE:
Name: {delegate['name']}
Title: {delegate['title']}
Company: {delegate['company']}
Sector: {delegate['sector']}
Objectives: {delegate['objectives']}
Interested Sectors: {', '.join(delegate['interested_sectors'])}

Analyze the synergy between this user and delegate. Provide:

**Alignment Areas:**
- List 2-3 key areas where their sectors, objectives, or interests align

**Collaboration Opportunities:**
- Identify 2-3 specific ways they could work together

**Recommended Talking Points:**
- Suggest 3-4 concrete topics for their first meeting

**Next Steps:**
- Recommend immediate actions

Keep the response under 250 words, professional, and actionable. Use markdown formatting."""

            response = gemini_model.generate_content(prompt)
            analysis = response.text

            # Add contact information
            analysis += f"\n\n**Contact Information:**\nEmail: {delegate['email']}\nPhone: {delegate.get('phone', 'Contact via Brisbane City Council')}"

            return analysis

        except Exception as e:
            print(f"[WARNING] Gemini API error: {e}. Using simple analysis.")

    # Fallback to simple analysis
    analysis = f"""**Alignment Areas:**
- {delegate['sector']} sector alignment
- Shared interest in {', '.join(delegate['interested_sectors'][:2])}

**Collaboration Opportunities:**
{delegate['objectives'][:200]}...

**Recommended Talking Points:**
1. Discuss mutual interests in {delegate['sector']}
2. Explore partnership opportunities
3. Share expertise and best practices

**Contact Information:**
Email: {delegate['email']}
Phone: {delegate.get('phone', 'Via Brisbane City Council')}
"""
    return analysis


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html', delegate_count=len(DELEGATES))


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and matching"""
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get form data
        user_name = request.form.get('name', '').strip()
        user_company = request.form.get('company', '').strip()
        user_email = request.form.get('email', '').strip()
        user_industry = request.form.get('industry', '').strip()

        if not user_name or not user_company:
            return jsonify({'error': 'Name and company are required'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)

        print(f"[UPLOAD] File saved: {safe_filename}")

        # Extract text from file
        if filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(filepath)
        elif filename.lower().endswith('.docx'):
            extracted_text = extract_text_from_docx(filepath)
        else:
            os.remove(filepath)  # Clean up
            return jsonify({'error': 'Unsupported file format. Please upload PDF or DOCX'}), 400

        if not extracted_text or len(extracted_text) < 50:
            os.remove(filepath)
            return jsonify({'error': 'Could not extract text from file. Please check the file format.'}), 400

        # Combine all user information for matching
        full_profile = f"""
Name: {user_name}
Company: {user_company}
Email: {user_email}
Industry: {user_industry}

Profile Content:
{extracted_text[:2000]}  # Limit to first 2000 chars for performance
"""

        # Perform matching
        user_info = {
            'name': user_name,
            'company': user_company,
            'email': user_email,
            'industry': user_industry,
            'uploaded_file': filename
        }

        matches = match_delegates(full_profile, user_info)

        # Add synergy analysis to each match
        for i, match in enumerate(matches, 1):
            try:
                print(f"[ANALYSIS] Generating synergy analysis for match {i}...")
                match['synergy_analysis'] = generate_synergy_analysis_simple(
                    full_profile,
                    match['delegate']
                )
                print(f"[OK] Analysis {i} complete")
            except Exception as e:
                print(f"[ERROR] Analysis {i} failed: {e}")
                import traceback
                traceback.print_exc()
                # Use fallback simple analysis
                match['synergy_analysis'] = f"""**Alignment Areas:**
- {match['delegate']['sector']} sector alignment

**Collaboration Opportunities:**
{match['delegate']['objectives'][:150]}...

**Contact Information:**
Email: {match['delegate']['email']}
Phone: {match['delegate'].get('phone', 'Via Brisbane City Council')}
"""

        # Store matches in Notion
        notion_success = 0
        for i, match in enumerate(matches, 1):
            try:
                print(f"[NOTION] Storing match {i} in Notion...")
                if store_match_in_notion(user_info, match, rank=i):
                    notion_success += 1
                    print(f"[OK] Match {i} stored in Notion")
                else:
                    print(f"[WARNING] Match {i} not stored in Notion")
            except Exception as e:
                print(f"[ERROR] Notion storage {i} failed: {e}")
                import traceback
                traceback.print_exc()

        if notion_success > 0:
            print(f"[NOTION] Stored {notion_success}/{len(matches)} matches in Notion")
        else:
            print("[WARNING] No matches stored in Notion")

        # Prepare response
        response_data = {
            'success': True,
            'user': user_info,
            'matches': [
                {
                    'rank': i + 1,
                    'name': m['delegate']['name'],
                    'title': m['delegate']['title'],
                    'company': m['delegate']['company'],
                    'sector': m['delegate']['sector'],
                    'score': m['score'],
                    'email': m['delegate']['email'],
                    'phone': m['delegate'].get('phone', 'Contact via Brisbane City Council'),
                    'objectives': m['delegate']['objectives'],
                    'interested_sectors': m['delegate']['interested_sectors'],
                    'synergy_analysis': m['synergy_analysis']
                }
                for i, m in enumerate(matches)
            ],
            'timestamp': datetime.now().isoformat()
        }

        # Save results to file for report generation
        results_filename = f"{timestamp}_{user_name.replace(' ', '_')}_results.json"
        results_path = os.path.join(app.config['UPLOAD_FOLDER'], results_filename)
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Matching complete for {user_name}")

        return jsonify(response_data)

    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF report for matches"""
    try:
        print("[PDF] Received PDF download request")
        data = request.get_json()
        print(f"[PDF] Request data keys: {data.keys() if data else 'No data'}")

        if not data or 'user' not in data or 'matches' not in data:
            error_msg = f"Missing user or matches data. Received: {list(data.keys()) if data else 'No data'}"
            print(f"[PDF ERROR] {error_msg}")
            return jsonify({'error': error_msg}), 400

        user_info = data['user']
        matches = data['matches']

        print(f"[PDF] Generating PDF report for {user_info.get('name', 'Unknown')}")
        print(f"[PDF] Number of matches: {len(matches)}")

        # Generate PDF
        pdf_buffer = generate_match_report_pdf(user_info, matches)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = user_info.get('name', 'User').replace(' ', '_')
        filename = f"Brisbane_Matches_{safe_name}_{timestamp}.pdf"

        print(f"[PDF] PDF generated successfully: {filename}")

        # Return PDF as attachment
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"[ERROR] PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


@app.route('/download_report/<filename>')
def download_report(filename):
    """Download JSON results (legacy)"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delegates')
def get_delegates():
    """API endpoint to get all delegates (for testing)"""
    return jsonify({
        'total': len(DELEGATES),
        'delegates': [
            {
                'name': d['name'],
                'company': d['company'],
                'sector': d['sector']
            }
            for d in DELEGATES
        ]
    })


@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    sectors = {}
    for delegate in DELEGATES:
        sector = delegate['sector']
        sectors[sector] = sectors.get(sector, 0) + 1

    return jsonify({
        'total_delegates': len(DELEGATES),
        'sectors': sectors,
        'version': '1.0.0',
        'event': 'Boldly Brisbane Forum & APCS 2025'
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Brisbane Business Bridge AI")
    print("AI-Powered Delegate Matching System")
    print("=" * 60)
    print(f"Delegates loaded: {len(DELEGATES)}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("=" * 60)
    print("\nStarting server...")

    # Get port from environment (Railway sets this)
    port = int(os.getenv('PORT', 5000))
    print(f"Server will run on port: {port}")
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
