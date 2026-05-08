"""
roadmap.py — AI Resume Screener
Generates a smart, personalized learning roadmap based on missing skills.
"""
 
from recommender import SKILL_RESOURCES, PRIORITY_ORDER
 
 
def generate_roadmap(missing_skills: list, total_months: int = 3) -> dict:
    """
    Generate a phased learning roadmap for missing skills.
 
    Strategy:
    - Phase 1 (Month 1): Very High + High priority foundational skills
    - Phase 2 (Month 2): High + Medium priority skills
    - Phase 3 (Month 3): Medium skills + projects + portfolio polish
 
    Returns a dict with phases, each containing tasks and milestones.
    """
    if not missing_skills:
        return _no_gap_roadmap()
 
    # Classify skills by priority
    very_high, high, medium, low, unknown = [], [], [], [], []
 
    for skill in missing_skills:
        sk = skill.lower()
        priority = SKILL_RESOURCES.get(sk, {}).get("priority", "Medium")
        if priority == "Very High":
            very_high.append(skill)
        elif priority == "High":
            high.append(skill)
        elif priority == "Medium":
            medium.append(skill)
        elif priority == "Low":
            low.append(skill)
        else:
            unknown.append(skill)
 
    phase1_skills = very_high + high[:3]
    phase2_skills = high[3:] + medium[:3]
    phase3_skills = medium[3:] + low + unknown
 
    roadmap = {
        "summary": _roadmap_summary(missing_skills, total_months),
        "phases": [
            _build_phase(
                number=1,
                label="Foundation Sprint",
                emoji="🚀",
                skills=phase1_skills,
                focus="Core skills that recruiters filter on first",
                milestone="Complete 1 hands-on project per skill learned",
                week_hint="Aim for 1–2 hrs/day",
            ),
            _build_phase(
                number=2,
                label="Build & Apply",
                emoji="🔨",
                skills=phase2_skills,
                focus="Supporting skills + integrate into real projects",
                milestone="Build 1 portfolio project combining multiple skills",
                week_hint="Join Kaggle / GitHub / Hackathon",
            ),
            _build_phase(
                number=3,
                label="Polish & Launch",
                emoji="🏆",
                skills=phase3_skills,
                focus="Final skills + resume & LinkedIn update",
                milestone="Deploy a full project online & update resume",
                week_hint="Apply to 5 jobs per week",
            ),
        ],
        "tips": [
            "✅ Learn in public — post progress on LinkedIn weekly",
            "✅ Build GitHub portfolio with at least 3 pinned projects",
            "✅ Get certifications for high-priority skills (AWS, Google, etc.)",
            "✅ Practice LeetCode/HackerRank alongside skill learning",
            "✅ Network — comment on LinkedIn posts in your target domain",
        ],
    }
 
    return roadmap
 
 
def _build_phase(number, label, emoji, skills, focus, milestone, week_hint) -> dict:
    tasks = []
    for skill in skills:
        sk = skill.lower()
        info = SKILL_RESOURCES.get(sk, {})
        course = info.get("courses", ["Search on Coursera or YouTube"])[0]
        time   = info.get("time", "2–4 weeks")
        tasks.append({
            "skill":  skill,
            "action": f"Learn {skill}",
            "course": course,
            "time":   time,
        })
 
    return {
        "phase":     number,
        "label":     f"Phase {number}: {label}",
        "emoji":     emoji,
        "month":     f"Month {number}",
        "skills":    skills,
        "tasks":     tasks,
        "focus":     focus,
        "milestone": milestone,
        "week_hint": week_hint,
        "empty":     len(skills) == 0,
    }
 
 
def _roadmap_summary(missing_skills, months) -> str:
    count = len(missing_skills)
    return (
        f"You have {count} skill gap(s) to bridge. "
        f"This {months}-month roadmap prioritizes the highest-impact skills first, "
        "helping you become job-ready as fast as possible."
    )
 
 
def _no_gap_roadmap() -> dict:
    return {
        "summary": "🎉 No skill gaps detected! You're an excellent match for this job.",
        "phases": [],
        "tips": [
            "✅ Tailor your resume bullet points to the job description",
            "✅ Prepare for behavioral interviews (STAR method)",
            "✅ Research the company culture and recent news",
            "✅ Send a personalized cover letter",
        ],
    }