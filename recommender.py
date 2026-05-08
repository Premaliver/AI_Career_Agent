"""
recommender.py — AI Resume Screener
Provides curated learning resources for missing skills with priority levels.
"""
 
# ─────────────────────────────────────────────────────────────
# SKILL RESOURCE DATABASE
# Each entry: { "courses": [...], "projects": [...], "time": str, "priority": str }
# ─────────────────────────────────────────────────────────────
SKILL_RESOURCES = {
    "python": {
        "courses": [
            "Python for Everybody — Coursera (Dr. Chuck) 🌟",
            "100 Days of Code — Udemy (Angela Yu)",
            "CS50P — Harvard Free Course",
        ],
        "projects": ["CLI tool", "Web scraper", "Automation script"],
        "time": "4–6 weeks",
        "priority": "High",
        "docs": "https://docs.python.org/3/",
    },
    "machine learning": {
        "courses": [
            "Machine Learning Specialization — Coursera (Andrew Ng) 🌟",
            "Fast.ai Practical Deep Learning (Free)",
            "ML Crash Course — Google (Free)",
        ],
        "projects": ["House price predictor", "Spam classifier", "Movie recommender"],
        "time": "3–6 months",
        "priority": "High",
        "docs": "https://scikit-learn.org/stable/",
    },
    "deep learning": {
        "courses": [
            "Deep Learning Specialization — Coursera (Andrew Ng) 🌟",
            "PyTorch for Deep Learning — freeCodeCamp",
            "Fast.ai (Free)",
        ],
        "projects": ["Image classifier", "Sentiment analysis", "Face detection"],
        "time": "3–5 months",
        "priority": "High",
        "docs": "https://pytorch.org/docs/stable/",
    },
    "generative ai": {
        "courses": [
            "Generative AI for Everyone — Coursera (Andrew Ng) 🌟",
            "LangChain for LLM Apps — DeepLearning.AI (Free)",
            "Building LLM Apps — Hugging Face (Free)",
        ],
        "projects": ["RAG chatbot", "AI content generator", "Resume analyzer"],
        "time": "6–10 weeks",
        "priority": "Very High",
        "docs": "https://python.langchain.com/",
    },
    "nlp": {
        "courses": [
            "NLP Specialization — Coursera (DeepLearning.AI) 🌟",
            "Hugging Face NLP Course (Free)",
            "NLP with Python — NLTK Book (Free)",
        ],
        "projects": ["Text summarizer", "Chatbot", "Sentiment classifier"],
        "time": "2–4 months",
        "priority": "High",
        "docs": "https://huggingface.co/learn",
    },
    "react": {
        "courses": [
            "React — The Complete Guide — Udemy (Maximilian) 🌟",
            "Full Stack Open — University of Helsinki (Free)",
            "React Official Docs Tutorial (Free)",
        ],
        "projects": ["Todo app", "Weather dashboard", "E-commerce UI"],
        "time": "6–8 weeks",
        "priority": "High",
        "docs": "https://react.dev/",
    },
    "javascript": {
        "courses": [
            "JavaScript — The Complete Guide — Udemy 🌟",
            "The Odin Project (Free)",
            "freeCodeCamp JS Curriculum (Free)",
        ],
        "projects": ["Interactive quiz", "API-fetching app", "Mini game"],
        "time": "6–10 weeks",
        "priority": "High",
        "docs": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    },
    "typescript": {
        "courses": [
            "TypeScript — The Complete Developer Guide — Udemy 🌟",
            "TypeScript Handbook (Official, Free)",
            "Execute Program TypeScript Course",
        ],
        "projects": ["Typed REST API", "React + TS dashboard"],
        "time": "3–4 weeks",
        "priority": "Medium",
        "docs": "https://www.typescriptlang.org/docs/",
    },
    "sql": {
        "courses": [
            "SQL for Data Science — Coursera (UC Davis)",
            "SQLZoo — Interactive SQL (Free) 🌟",
            "Mode Analytics SQL Tutorial (Free)",
        ],
        "projects": ["Library DB", "Sales analytics query set", "Student management system"],
        "time": "3–5 weeks",
        "priority": "High",
        "docs": "https://www.w3schools.com/sql/",
    },
    "mongodb": {
        "courses": [
            "MongoDB University — M001 Basics (Free) 🌟",
            "The Complete MongoDB Developer — Udemy",
        ],
        "projects": ["Blog API", "E-commerce backend"],
        "time": "3–4 weeks",
        "priority": "Medium",
        "docs": "https://www.mongodb.com/docs/",
    },
    "aws": {
        "courses": [
            "AWS Cloud Practitioner Essentials — AWS Skill Builder (Free) 🌟",
            "Ultimate AWS Certified Developer — Udemy (Stephane Maarek)",
            "A Cloud Guru — AWS Path",
        ],
        "projects": ["Host static site on S3", "Lambda + API Gateway app", "EC2 deployment"],
        "time": "2–3 months",
        "priority": "Very High",
        "docs": "https://docs.aws.amazon.com/",
    },
    "docker": {
        "courses": [
            "Docker Mastery — Udemy (Bret Fisher) 🌟",
            "Play with Docker (Free interactive lab)",
            "Docker Official Getting Started (Free)",
        ],
        "projects": ["Dockerize Flask app", "Multi-container app with Compose"],
        "time": "2–3 weeks",
        "priority": "High",
        "docs": "https://docs.docker.com/",
    },
    "kubernetes": {
        "courses": [
            "Certified Kubernetes Administrator (CKA) Prep — KodeKloud 🌟",
            "Kubernetes for Developers — Udemy",
        ],
        "projects": ["Deploy containerized app to K8s", "Set up Helm chart"],
        "time": "4–8 weeks",
        "priority": "High",
        "docs": "https://kubernetes.io/docs/",
    },
    "git": {
        "courses": [
            "Git & GitHub Crash Course — freeCodeCamp (Free) 🌟",
            "Pro Git Book (Free)",
        ],
        "projects": ["Contribute to open source on GitHub"],
        "time": "1–2 weeks",
        "priority": "High",
        "docs": "https://git-scm.com/doc",
    },
    "data science": {
        "courses": [
            "IBM Data Science Professional Certificate — Coursera 🌟",
            "Data Science from Scratch — O'Reilly",
            "Kaggle Learn (Free)",
        ],
        "projects": ["EDA on Titanic dataset", "Stock price visualization", "Customer churn prediction"],
        "time": "4–6 months",
        "priority": "High",
        "docs": "https://www.kaggle.com/learn",
    },
    "tensorflow": {
        "courses": [
            "TensorFlow Developer Certificate — Coursera (DeepLearning.AI) 🌟",
            "TensorFlow Official Tutorials (Free)",
        ],
        "projects": ["MNIST classifier", "Transfer learning image classifier"],
        "time": "6–8 weeks",
        "priority": "High",
        "docs": "https://www.tensorflow.org/learn",
    },
    "flask": {
        "courses": [
            "Flask Mega-Tutorial — Miguel Grinberg (Free) 🌟",
            "REST APIs with Flask and Python — Udemy",
        ],
        "projects": ["Blog app", "REST API backend", "ML model API"],
        "time": "2–3 weeks",
        "priority": "Medium",
        "docs": "https://flask.palletsprojects.com/",
    },
    "django": {
        "courses": [
            "Django for Everybody — Coursera (Dr. Chuck) 🌟",
            "Official Django Tutorial (Free)",
        ],
        "projects": ["E-commerce site", "Social media clone"],
        "time": "4–6 weeks",
        "priority": "Medium",
        "docs": "https://docs.djangoproject.com/",
    },
    "power bi": {
        "courses": [
            "Microsoft Power BI Desktop — Udemy (Maven Analytics) 🌟",
            "Power BI Learning Path — Microsoft (Free)",
        ],
        "projects": ["Sales dashboard", "HR analytics report"],
        "time": "2–4 weeks",
        "priority": "Medium",
        "docs": "https://learn.microsoft.com/en-us/power-bi/",
    },
    "agile": {
        "courses": [
            "Agile Fundamentals — Coursera",
            "Scrum Fundamentals Certified (SFC) — Free Exam",
        ],
        "projects": ["Run a personal Kanban board on Notion/Trello"],
        "time": "1–2 weeks",
        "priority": "Medium",
        "docs": "https://www.scrum.org/resources/what-is-scrum",
    },
    "linux": {
        "courses": [
            "Linux Command Line Basics — Udacity (Free)",
            "The Linux Command Line — Book (Free PDF) 🌟",
            "OverTheWire Bandit (Free, hands-on)",
        ],
        "projects": ["Set up a personal Linux server", "Write bash automation scripts"],
        "time": "2–4 weeks",
        "priority": "High",
        "docs": "https://linuxcommand.org/",
    },
    "node.js": {
        "courses": [
            "Node.js, Express, MongoDB Bootcamp — Udemy (Jonas Schmedtmann) 🌟",
            "Node.js Official Docs (Free)",
        ],
        "projects": ["REST API", "Real-time chat with Socket.io"],
        "time": "4–6 weeks",
        "priority": "High",
        "docs": "https://nodejs.org/en/docs/",
    },
    "fastapi": {
        "courses": [
            "FastAPI Official Tutorial (Free) 🌟",
            "Building APIs with FastAPI — TestDriven.io",
        ],
        "projects": ["ML model serving API", "CRUD REST API"],
        "time": "1–2 weeks",
        "priority": "Medium",
        "docs": "https://fastapi.tiangolo.com/",
    },
}
 
PRIORITY_ORDER = {"Very High": 0, "High": 1, "Medium": 2, "Low": 3}
 
 
def recommend_skills(missing_skills: list) -> list[dict]:
    """
    Returns a sorted list of recommendation dicts for missing skills.
    Each dict: { skill, courses, projects, time, priority, docs }
    Sorted by priority (Very High → High → Medium → Low).
    Unknown skills get a generic entry.
    """
    recommendations = []
 
    for skill in missing_skills:
        skill_lower = skill.lower()
        if skill_lower in SKILL_RESOURCES:
            entry = SKILL_RESOURCES[skill_lower].copy()
            entry["skill"] = skill
        else:
            entry = {
                "skill": skill,
                "courses": [
                    f"Search '{skill}' on Coursera, Udemy, or YouTube",
                    f"Look for '{skill}' official documentation",
                ],
                "projects": [f"Build a small demo project using {skill}"],
                "time": "Varies",
                "priority": "Medium",
                "docs": f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial",
            }
        recommendations.append(entry)
 
    # Sort by priority
    recommendations.sort(key=lambda x: PRIORITY_ORDER.get(x.get("priority", "Medium"), 2))
    return recommendations