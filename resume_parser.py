"""
resume_parser.py — AI Resume Screener
Extracts text from PDF and detects skills with synonym-aware matching.
"""
 
import PyPDF2
import re
import logging
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# ─────────────────────────────────────────────
# MASTER SKILL DATABASE — extend freely
# ─────────────────────────────────────────────
SKILLS_DB = {
    # ── Programming Languages ──
    "python":           ["python", "py"],
    "java":             ["java", "java8", "java11", "java17"],
    "javascript":       ["javascript", "js", "es6", "es2015", "ecmascript"],
    "typescript":       ["typescript", "ts"],
    "c++":              ["c++", "cpp", "c plus plus"],
    "c#":               ["c#", "csharp", "c sharp", ".net"],
    "go":               ["golang", "go lang"],
    "rust":             ["rust"],
    "kotlin":           ["kotlin"],
    "swift":            ["swift"],
    "php":              ["php"],
    "ruby":             ["ruby", "ruby on rails", "rails"],
    "r":                ["r programming", " r ", "rstudio"],
    "scala":            ["scala"],
    "dart":             ["dart", "flutter"],
 
    # ── Web / Frontend ──
    "html":             ["html", "html5"],
    "css":              ["css", "css3"],
    "react":            ["react", "react.js", "reactjs"],
    "angular":          ["angular", "angularjs"],
    "vue":              ["vue", "vue.js", "vuejs"],
    "next.js":          ["next.js", "nextjs"],
    "tailwind css":     ["tailwind", "tailwindcss"],
    "bootstrap":        ["bootstrap"],
    "jquery":           ["jquery"],
    "webpack":          ["webpack"],
 
    # ── Backend / Frameworks ──
    "flask":            ["flask"],
    "django":           ["django"],
    "fastapi":          ["fastapi"],
    "node.js":          ["node.js", "nodejs", "node js", "express", "expressjs"],
    "spring boot":      ["spring boot", "spring framework"],
    "graphql":          ["graphql"],
    "rest api":         ["rest api", "restful", "rest", "api design"],
 
    # ── Databases ──
    "sql":              ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "mongodb":          ["mongodb", "mongo"],
    "redis":            ["redis"],
    "elasticsearch":    ["elasticsearch", "elastic search"],
    "firebase":         ["firebase"],
    "cassandra":        ["cassandra"],
 
    # ── AI / ML / Data ──
    "machine learning": ["machine learning", "ml", "sklearn", "scikit-learn", "scikit learn"],
    "deep learning":    ["deep learning", "dl", "neural network", "neural networks"],
    "nlp":              ["nlp", "natural language processing", "text mining"],
    "computer vision":  ["computer vision", "cv", "image processing", "opencv"],
    "tensorflow":       ["tensorflow", "tf"],
    "pytorch":          ["pytorch", "torch"],
    "keras":            ["keras"],
    "data science":     ["data science", "data scientist"],
    "data analysis":    ["data analysis", "data analytics", "data analyst"],
    "pandas":           ["pandas"],
    "numpy":            ["numpy"],
    "matplotlib":       ["matplotlib", "seaborn", "plotly"],
    "tableau":          ["tableau"],
    "power bi":         ["power bi", "powerbi"],
    "excel":            ["excel", "ms excel", "microsoft excel"],
    "statistics":       ["statistics", "statistical analysis", "hypothesis testing"],
    "generative ai":    ["generative ai", "genai", "llm", "large language model", "gpt", "chatgpt", "langchain"],
 
    # ── DevOps / Cloud ──
    "docker":           ["docker", "containerization"],
    "kubernetes":       ["kubernetes", "k8s"],
    "aws":              ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure":            ["azure", "microsoft azure"],
    "gcp":              ["gcp", "google cloud", "google cloud platform"],
    "ci/cd":            ["ci/cd", "cicd", "github actions", "jenkins", "gitlab ci"],
    "linux":            ["linux", "unix", "bash", "shell scripting", "shell script"],
    "terraform":        ["terraform", "iac", "infrastructure as code"],
    "git":              ["git", "github", "gitlab", "version control"],
 
    # ── Soft / Business Skills ──
    "agile":            ["agile", "scrum", "kanban", "sprint"],
    "project management": ["project management", "pmp", "prince2"],
    "communication":    ["communication skills", "verbal communication", "written communication"],
    "leadership":       ["leadership", "team lead", "team leadership"],
    "problem solving":  ["problem solving", "analytical thinking", "critical thinking"],
 
    # ── Design / UX ──
    "figma":            ["figma"],
    "ui/ux":            ["ui/ux", "ui ux", "user interface", "user experience", "ux design"],
    "adobe xd":         ["adobe xd"],
    "photoshop":        ["photoshop", "adobe photoshop"],
 
    # ── Other Tech ──
    "cybersecurity":    ["cybersecurity", "cyber security", "ethical hacking", "penetration testing"],
    "blockchain":       ["blockchain", "solidity", "web3", "smart contract"],
    "iot":              ["iot", "internet of things", "embedded systems", "arduino"],
    "salesforce":       ["salesforce", "crm"],
    "sap":              ["sap"],
    "excel vba":        ["vba", "excel vba", "macro"],
}
 
 
def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
        logger.info(f"Extracted {len(text)} characters from {file_path}")
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
    return text
 
 
def clean_text(text: str) -> str:
    """Lowercase and normalize text for skill matching."""
    text = text.lower()
    text = re.sub(r'[^\w\s\+\#\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text
 
 
def extract_skills(text: str) -> list[str]:
    """
    Extract skills from text using synonym-aware multi-word matching.
    Returns a deduplicated, sorted list of canonical skill names.
    """
    cleaned = clean_text(text)
    found = set()
 
    for canonical_skill, keywords in SKILLS_DB.items():
        for kw in keywords:
            # Use word-boundary aware search for single-word keywords
            if ' ' in kw:
                if kw in cleaned:
                    found.add(canonical_skill)
                    break
            else:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, cleaned):
                    found.add(canonical_skill)
                    break
 
    return sorted(list(found))
 
 
def extract_experience_years(text: str) -> int:
    """Try to extract years of experience from resume text."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
    ]
    text_lower = text.lower()
    for pat in patterns:
        match = re.search(pat, text_lower)
        if match:
            return int(match.group(1))
    return 0
 
 
def extract_education(text: str) -> str:
    """Detect highest education level mentioned."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["phd", "ph.d", "doctorate", "doctoral"]):
        return "PhD"
    if any(w in text_lower for w in ["master", "m.sc", "mba", "m.tech", "m.e."]):
        return "Masters"
    if any(w in text_lower for w in ["bachelor", "b.sc", "b.e.", "b.tech", "b.com", "b.a."]):
        return "Bachelors"
    if any(w in text_lower for w in ["diploma", "polytechnic"]):
        return "Diploma"
    return "Not specified"