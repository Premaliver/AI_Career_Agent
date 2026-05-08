"""
agent.py — AI Resume Screener
Generates a structured, personalized AI career advice report.
"""

from recommender import SKILL_RESOURCES


def ai_agent_response(
    resume_skills: list,
    missing_skills: list,
    match_result: dict,
    experience_years: int = 0,
    education: str = "Not specified",
) -> dict:
    """
    Generate a structured AI career advice report.

    Args:
        resume_skills   : Skills found in resume
        missing_skills  : Skills required by job but missing in resume
        match_result    : Output dict from matcher.match_skills()
        experience_years: Years of experience extracted from resume
        education       : Detected education level

    Returns:
        A dict with sections: headline, profile_summary, strengths,
        gaps_analysis, quick_wins, long_term, interview_tips, application_advice
    """
    percent    = match_result.get("match_percent", 0)
    fit_level  = match_result.get("fit_level", "Unknown")
    fit_emoji  = match_result.get("fit_emoji", "⚪")
    matched    = match_result.get("matched", [])
    extra      = match_result.get("extra", [])

    report = {
        "headline":           _headline(fit_level, fit_emoji, percent),
        "profile_summary":    _profile_summary(percent, fit_level, experience_years, education, resume_skills),
        "strengths":          _strengths(matched, extra, experience_years),
        "gaps_analysis":      _gaps_analysis(missing_skills),
        "quick_wins":         _quick_wins(missing_skills),
        "long_term":          _long_term(missing_skills, fit_level),
        "interview_tips":     _interview_tips(matched, fit_level),
        "application_advice": _application_advice(fit_level, percent),
        "score_breakdown": {
            "match_score":   percent,
            "skills_count":  len(resume_skills),
            "matched_count": len(matched),
            "missing_count": len(missing_skills),
            "experience":    experience_years,
            "education":     education,
        },
    }
    return report


# ── Section builders ──────────────────────────────────────────────────────────

def _headline(fit_level: str, emoji: str, percent: float) -> str:
    headlines = {
        "Excellent": f"{emoji} Outstanding Match — You're a Top Candidate!",
        "Good":      f"{emoji} Strong Profile — Minor Gaps to Bridge",
        "Moderate":  f"{emoji} Promising Candidate — Targeted Upskilling Needed",
        "Needs Work": f"{emoji} Developing Profile — Strategic Learning Required",
        "Low":       f"{emoji} Early Stage — Significant Growth Opportunity Ahead",
    }
    return headlines.get(fit_level, f"{emoji} Match Analysis: {percent}%")


def _profile_summary(percent, fit_level, years, education, skills) -> str:
    skill_count = len(skills)
    exp_note = f"with {years}+ years of experience" if years > 0 else "at an early career stage"
    edu_note  = f"Educational background: {education}." if education != "Not specified" else ""

    if fit_level == "Excellent":
        return (
            f"You are an exceptionally strong candidate {exp_note}, holding {skill_count} relevant skills "
            f"and matching {percent}% of the job requirements. {edu_note} "
            "Your profile stands out — focus on crafting a compelling narrative in your cover letter."
        )
    elif fit_level == "Good":
        return (
            f"You have a solid foundation {exp_note} with {skill_count} relevant skills, "
            f"matching {percent}% of requirements. {edu_note} "
            "A few targeted additions to your skillset will make you highly competitive."
        )
    elif fit_level == "Moderate":
        return (
            f"You have a developing profile {exp_note} with {skill_count} skills, "
            f"matching {percent}% of requirements. {edu_note} "
            "With focused learning over the next 2–3 months, you can significantly improve your candidacy."
        )
    else:
        return (
            f"Your current profile matches {percent}% of this role's requirements {exp_note}. "
            f"{edu_note} This is a growth opportunity — a structured learning plan will help you "
            "become job-ready within 3–6 months."
        )


def _strengths(matched: list, extra: list, years: int) -> list[str]:
    points = []
    if matched:
        points.append(f"✅ You already have {len(matched)} job-required skill(s): {', '.join(matched[:5])}{'...' if len(matched) > 5 else ''}.")
    if extra:
        points.append(f"⭐ You bring {len(extra)} bonus skill(s) beyond the job requirements: {', '.join(extra[:4])}{'...' if len(extra) > 4 else ''} — highlight these as added value.")
    if years >= 5:
        points.append(f"💼 {years}+ years of experience is a strong differentiator — emphasize this in interviews.")
    elif years >= 2:
        points.append(f"💼 {years} years of experience gives you practical credibility.")
    if not points:
        points.append("📚 You're at the beginning of your journey — every expert started here!")
    return points


def _gaps_analysis(missing: list) -> list[dict]:
    if not missing:
        return [{
            "skill":    "None",
            "priority": "—",
            "time":     "—",
            "impact":   "✅ No gaps detected — great match!",
        }]

    result = []
    for skill in missing:
        sk = skill.lower()
        info = SKILL_RESOURCES.get(sk, {})
        priority = info.get("priority", "Medium")
        time = info.get("time", "2–4 weeks")
        impact_map = {
            "Very High": "🔴 Critical — recruiters often auto-reject without this",
            "High":      "🟠 Important — significantly improves your candidacy",
            "Medium":    "🟡 Useful — adds competitive advantage",
            "Low":       "🟢 Nice to have — learn when time permits",
        }
        result.append({
            "skill":    skill,
            "priority": priority,
            "time":     time,
            "impact":   impact_map.get(priority, "🟡 Useful"),
        })

    result.sort(key=lambda x: {"Very High": 0, "High": 1, "Medium": 2, "Low": 3}.get(x["priority"], 2))
    return result


def _quick_wins(missing: list) -> list[str]:
    """Skills learnable in <3 weeks — fast resume boosters."""
    quick = []
    for skill in missing:
        sk = skill.lower()
        info = SKILL_RESOURCES.get(sk, {})
        time_str = info.get("time", "")
        try:
            weeks = int(time_str.split("–")[0].replace("weeks", "").replace("week", "").strip())
            if weeks <= 3:
                course = info.get("courses", ["Search online"])[0]
                quick.append(f"⚡ {skill} ({time_str}) — Start with: {course}")
        except Exception:
            pass
    return quick if quick else ["No quick wins detected — all gaps require sustained effort."]


def _long_term(missing: list, fit_level: str) -> list[str]:
    advice = []
    if fit_level in ("Needs Work", "Low"):
        advice.append("🎯 Set a 90-day learning goal and track weekly progress.")
        advice.append("📁 Build a GitHub portfolio with 3+ projects before applying.")
        advice.append("🤝 Start networking now — connect with professionals in your target role on LinkedIn.")
    else:
        advice.append("🎯 Focus on the top 2–3 missing skills for the highest ROI.")
        advice.append("📁 Add a project showcasing each new skill to your portfolio.")
    advice.append("📜 Pursue relevant certifications (AWS, Google, Microsoft, etc.) for credibility.")
    advice.append("🗣️ Practice mock interviews on Pramp, Interviewing.io, or with a peer.")
    return advice


def _interview_tips(matched: list, fit_level: str) -> list[str]:
    tips = [
        "📝 Prepare STAR-format stories (Situation, Task, Action, Result) for each matched skill.",
        f"💡 Lead with your strongest skills: {', '.join(matched[:3]) if matched else 'your top technical skills'}.",
        "📊 Quantify your achievements — 'Improved performance by 30%' beats 'improved performance'.",
        "🔍 Research the company's tech stack and recent news before every interview.",
        "❓ Prepare 3 thoughtful questions to ask the interviewer.",
    ]
    if fit_level in ("Excellent", "Good"):
        tips.append("🚀 You can negotiate from strength — know your market rate on Glassdoor/Levels.fyi.")
    return tips


def _application_advice(fit_level: str, percent: float) -> list[str]:
    if fit_level == "Excellent":
        return [
            "📧 Apply immediately — you are a strong candidate.",
            "✍️ Write a personalized cover letter referencing specific job requirements.",
            "🔗 Request referrals from your network at this company if possible.",
        ]
    elif fit_level == "Good":
        return [
            "📧 Apply now while learning the 1–2 missing skills in parallel.",
            "✍️ Emphasize transferable skills and project experience in your cover letter.",
            "📌 Tailor your resume bullet points to mirror the job description keywords.",
        ]
    elif fit_level == "Moderate":
        return [
            "📅 Apply in 4–6 weeks after building the highest-priority missing skills.",
            "🛠️ In the meantime, build a relevant project to demonstrate initiative.",
            "📌 Customize your resume for each application — use keywords from the job description.",
        ]
    else:
        return [
            "📅 Target applying in 2–3 months after focused upskilling.",
            "🛠️ Build 2–3 projects and publish them on GitHub before applying.",
            "📌 Consider junior or internship roles at this company while building toward the target role.",
        ]