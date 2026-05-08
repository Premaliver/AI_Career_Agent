"""
app.py — AI Resume Screener
Professional Flask backend with validation, error handling, and structured data flow.
"""

import os
import logging
import uuid
from pathlib import Path

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import requests as http_requests

from resume_parser import (
    extract_text_from_pdf,
    extract_skills,
    extract_experience_years,
    extract_education,
)
from matcher import match_skills
from recommender import recommend_skills
from roadmap import generate_roadmap
from agent import ai_agent_response
from job_automation import run_job_automation
from dotenv import load_dotenv
load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── App config ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ai-resume-screener-dev-key-change-in-prod")

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

ALLOWED_EXTENSIONS = {"pdf"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_filename(original: str) -> str:
    """Generate a unique safe filename to avoid collisions."""
    ext = Path(original).suffix
    return f"{uuid.uuid4().hex}{ext}"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_resume():
    # ── Input validation ──────────────────────────────────────────────────────
    if "resume" not in request.files:
        flash("❌ No file uploaded. Please select your resume PDF.", "error")
        return redirect(url_for("home"))

    file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()
    if not job_description:
        job_description = (
            "General role inferred from resume. "
            "The automation engine will use the parsed resume profile for job discovery."
        )

    if file.filename == "":
        flash("❌ No file selected.", "error")
        return redirect(url_for("home"))

    if not allowed_file(file.filename):
        flash("❌ Only PDF files are supported.", "error")
        return redirect(url_for("home"))

    if not job_description or len(job_description) < 30:
        flash("❌ Please provide a detailed job description (at least 30 characters).", "error")
        return redirect(url_for("home"))

    # ── Save uploaded file securely ───────────────────────────────────────────
    filename = safe_filename(file.filename)
    filepath = UPLOAD_FOLDER / filename

    try:
        file.save(str(filepath))
        logger.info(f"Resume saved: {filepath}")
    except Exception as e:
        logger.error(f"File save failed: {e}")
        flash("❌ Failed to save the uploaded file. Please try again.", "error")
        return redirect(url_for("home"))

    # ── Processing pipeline ───────────────────────────────────────────────────
    try:
        # 1. Parse resume
        resume_text    = extract_text_from_pdf(str(filepath))
        resume_skills  = extract_skills(resume_text)
        experience_yrs = extract_experience_years(resume_text)
        education      = extract_education(resume_text)

        if not resume_text.strip():
            flash("❌ Could not extract text from your PDF. Try a text-based (not scanned) PDF.", "error")
            return redirect(url_for("home"))

        # 2. Parse job description
        job_skills = extract_skills(job_description)

        # 3. Match skills
        match_result = match_skills(resume_skills, job_skills)

        # 4. Recommendations
        recommendations = recommend_skills(match_result["missing"])

        # 5. Roadmap
        roadmap = generate_roadmap(match_result["missing"])

        # 6. AI Agent report
        agent_output = ai_agent_response(
            resume_skills  = resume_skills,
            missing_skills = match_result["missing"],
            match_result   = match_result,
            experience_years = experience_yrs,
            education      = education,
        )

        # 7. Resume-to-Jobs Automation Engine (additive and non-blocking)
        job_automation = {"profile": None, "matches": [], "connector_errors": [], "sources_used": []}
        try:
            job_automation = run_job_automation(
                resume_text=resume_text,
                resume_skills=resume_skills,
                user_id=request.form.get("user_id", "anonymous"),
                email=request.form.get("email") or None,
                preferred_role=request.form.get("preferred_role") or None,
                location=request.form.get("location") or None,
                work_mode=request.form.get("work_mode") or None,
                limit=8,
            )
        except Exception as e:
            logger.warning(f"Job automation skipped: {e}", exc_info=True)

        logger.info(
            f"Analysis complete — match: {match_result['match_percent']}%, "
            f"skills: {len(resume_skills)}, missing: {len(match_result['missing'])}"
        )

    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        flash(f"❌ Analysis failed: {str(e)}", "error")
        return redirect(url_for("home"))
    finally:
        # Clean up uploaded file
        try:
            filepath.unlink(missing_ok=True)
        except Exception:
            pass

    # ── Render results ────────────────────────────────────────────────────────
    # Guarantee roadmap always has the keys the template expects
    safe_roadmap = {
        "summary": roadmap.get("summary", ""),
        "phases":  roadmap.get("phases", []),
        "tips":    roadmap.get("tips", []),
    }

    return render_template("result.html", result={
        "resume_skills":   resume_skills,
        "job_skills":      job_skills,
        "match":           match_result,
        "recommendations": recommendations,
        "roadmap":         safe_roadmap,
        "agent":           agent_output,
        "experience":      experience_yrs,
        "education":       education,
        "job_automation":  job_automation,
    })


@app.route("/chat", methods=["POST"])
def chat():
    """
    AI Career Chatbot endpoint (Groq API).
    """
    try:
        body = request.get_json(force=True)

        messages = body.get("messages", [])
        system_prompt = body.get("system", "You are a helpful AI Career Assistant.")

        if not messages:
            return jsonify({"reply": "Koi message nahi mila."}), 400

        # Keep last 10 messages
        messages = messages[-10:]

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return jsonify({"reply": "⚠️ GROQ_API_KEY set nahi hai .env mein."}), 500

        # Ensure correct format
        groq_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            if "role" in msg and "content" in msg:
                groq_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        response = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": groq_messages,
                "temperature": 0.7,
                "max_tokens": 512,
            },
            timeout=20,
        )

        if response.status_code != 200:
            logger.error(f"Groq API error {response.status_code}: {response.text}")
            return jsonify({"reply": "AI response nahi mila. Thodi der baad try karein."}), 502

        data = response.json()

        # Safe extraction (no crash)
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No response")

        return jsonify({"reply": reply})

    except http_requests.Timeout:
        return jsonify({"reply": "⏱️ Response time out ho gaya. Dobara try karein."}), 504

    except http_requests.ConnectionError:
        logger.error("Chat connection error: unable to reach Groq API", exc_info=True)
        return jsonify({
            "reply": "Groq API se connect nahi ho pa raha. Internet/firewall check karein, aur GROQ_API_KEY valid hai yeh confirm karein."
        }), 503

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({"reply": "Kuch gadbad ho gayi. Baad mein try karein."}), 500
    


@app.route("/health")
def health():
    """Health check endpoint for deployment monitoring."""
    return jsonify({"status": "ok", "service": "AI Resume Screener"})


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    flash("❌ File too large. Maximum size is 10 MB.", "error")
    return redirect(url_for("home"))


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    flash("❌ Internal server error. Please try again.", "error")
    return redirect(url_for("home"))


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    logger.info(f"🚀 Starting AI Resume Screener on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
    
