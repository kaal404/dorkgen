"""Categories (with subcategories) and use-case profiles.

Every ``packs`` list below is validated at import time (see the bottom of
this file) against ``keywordpacks.KEYWORD_PACKS`` so a profile can never
silently reference a pack that doesn't exist — that was a real bug in the
original codebase (``ai_services``, ``react``, ``angular`` were referenced
but undefined; see AUDIT.md).
"""
from __future__ import annotations

from .keywordpacks import KEYWORD_PACKS

CATEGORIES: dict[str, dict[str, object]] = {
    "cloud": {"name": "☁️  Cloud", "desc": "Cloud infrastructure dorks", "subs": {
        "aws": "AWS", "azure": "Azure", "gcp": "Google Cloud",
        "firebase": "Firebase", "cloudflare": "Cloudflare"}},
    "secrets": {"name": "🔑  Secrets", "desc": "Secret & credential dorks", "subs": {
        "api_keys": "API Keys", "passwords": "Passwords", "tokens": "Tokens",
        "private_keys": "Private Keys", "credentials": "Credentials"}},
    "authentication": {"name": "🔐  Authentication", "desc": "Authentication dorks", "subs": {
        "login_pages": "Login Pages", "admin_panels": "Admin Panels",
        "oauth": "OAuth", "sso": "SSO", "jwt": "JWT"}},
    "apis": {"name": "🔌  APIs", "desc": "API & endpoint dorks", "subs": {
        "rest": "REST", "graphql": "GraphQL", "swagger": "Swagger/OpenAPI"}},
    "source_code": {"name": "📄  Source Code", "desc": "Source code dorks", "subs": {
        "git_exposure": "Git Exposure", "github": "GitHub",
        "gitlab": "GitLab", "bitbucket": "Bitbucket"}},
    "devops": {"name": "🔄  DevOps", "desc": "DevOps pipeline dorks", "subs": {
        "docker": "Docker", "kubernetes": "Kubernetes", "terraform": "Terraform",
        "jenkins": "Jenkins", "ci_cd": "CI/CD"}},
    "config_files": {"name": "⚙️  Configuration Files", "desc": "Config file dorks", "subs": {
        "env_files": ".env Files", "web_configs": "Web Configs",
        "app_configs": "App Configs", "db_configs": "DB Configs"}},
    "documents": {"name": "📝  Documents", "desc": "Document dorks", "subs": {
        "pdfs": "PDFs", "spreadsheets": "Spreadsheets", "word_docs": "Word Docs"}},
    "backups": {"name": "💾  Backups", "desc": "Backup file dorks", "subs": {
        "database_backups": "DB Backups", "file_backups": "File Backups",
        "system_backups": "System Backups"}},
    "databases": {"name": "🗄  Databases", "desc": "Database exposure dorks", "subs": {
        "mysql": "MySQL", "postgresql": "PostgreSQL", "mongodb": "MongoDB",
        "redis": "Redis", "elasticsearch": "Elasticsearch"}},
    "logs": {"name": "📋  Logs", "desc": "Log file dorks", "subs": {
        "access_logs": "Access Logs", "error_logs": "Error Logs", "audit_logs": "Audit Logs"}},
    "certificates": {"name": "🔒  Certificates", "desc": "SSL/TLS dorks", "subs": {
        "ssl_certs": "SSL Certs", "private_keys": "Private Keys"}},
    "frameworks": {"name": "📚  Frameworks", "desc": "Framework dorks", "subs": {
        "laravel": "Laravel", "django": "Django", "spring": "Spring Boot",
        "nodejs": "Node.js", "react": "React", "angular": "Angular", "nextjs": "Next.js"}},
    "cms": {"name": "🧩  CMS", "desc": "Content management system dorks", "subs": {
        "wordpress": "WordPress"}},
    "containers": {"name": "🐳  Containers", "desc": "Container dorks", "subs": {
        "docker_exposure": "Docker Exposure", "k8s_dashboards": "K8s Dashboards",
        "container_registries": "Container Registries"}},
    "ai_services": {"name": "🤖  AI Services", "desc": "AI/ML dorks", "subs": {
        "openai": "OpenAI", "huggingface": "HuggingFace", "anthropic": "Anthropic"}},
    "email": {"name": "✉️  Email", "desc": "Email & messaging service dorks", "subs": {
        "smtp": "SMTP", "transactional": "Transactional email providers"}},
    "sector": {"name": "🏥  Sector-Specific", "desc": "Industry-specific exposure dorks", "subs": {
        "medical": "Medical/Healthcare", "finance": "Finance/Banking",
        "government": "Government", "education": "Education"}},
}

PROFILES: dict[str, dict[str, object]] = {
    "bug_bounty": {"name": "🎯 Bug Bounty", "desc": "Bug bounty hunting",
        "cats": ["secrets", "cloud", "authentication", "apis", "source_code", "devops", "config_files"],
        "packs": ["secrets", "api", "auth", "jwt", "passwords", "aws", "docker", "git"]},
    "red_team": {"name": "🔴 Red Team", "desc": "Offensive security",
        "cats": ["cloud", "secrets", "authentication", "apis", "devops", "config_files", "certificates"],
        "packs": ["aws", "azure", "gcp", "secrets", "passwords", "api", "auth", "docker", "kubernetes", "terraform"]},
    "blue_team": {"name": "🔵 Blue Team", "desc": "Defensive monitoring",
        "cats": ["cloud", "secrets", "config_files", "logs", "certificates"],
        "packs": ["secrets", "config_files", "monitoring"]},
    "enterprise": {"name": "🏢 Enterprise", "desc": "Enterprise assessment",
        "cats": ["cloud", "secrets", "authentication", "apis", "devops", "frameworks", "containers"],
        "packs": ["aws", "azure", "gcp", "secrets", "api", "auth", "docker", "kubernetes", "monitoring"]},
    "saas": {"name": "☁️  SaaS", "desc": "SaaS assessment",
        "cats": ["cloud", "secrets", "authentication", "apis", "devops", "containers", "ai_services"],
        "packs": ["aws", "azure", "gcp", "secrets", "api", "auth", "docker", "kubernetes", "ai_services"]},
    "healthcare": {"name": "🏥 Healthcare", "desc": "Healthcare/HIPAA",
        "cats": ["secrets", "config_files", "documents", "databases", "certificates", "sector"],
        "packs": ["secrets", "passwords", "config_files", "database", "medical"]},
    "government": {"name": "🏛  Government", "desc": "Government sector",
        "cats": ["secrets", "authentication", "documents", "certificates", "sector"],
        "packs": ["secrets", "auth", "passwords", "config_files", "government"]},
    "banking": {"name": "🏦 Banking", "desc": "Financial services",
        "cats": ["secrets", "authentication", "apis", "config_files", "databases", "logs", "certificates", "sector"],
        "packs": ["secrets", "passwords", "api", "auth", "jwt", "database", "monitoring", "finance"]},
    "cloud": {"name": "☁️  Cloud Only", "desc": "Cloud infrastructure",
        "cats": ["cloud", "secrets", "devops", "containers"],
        "packs": ["aws", "azure", "gcp", "cloudflare", "docker", "kubernetes", "terraform"]},
    "startup": {"name": "🚀 Startup", "desc": "Startup review",
        "cats": ["cloud", "secrets", "authentication", "apis", "devops"],
        "packs": ["aws", "gcp", "secrets", "api", "auth", "docker", "git"]},
    "education": {"name": "🎓 Education", "desc": "Education sector",
        "cats": ["secrets", "config_files", "documents", "sector"],
        "packs": ["secrets", "config_files", "education"]},
    "osint": {"name": "🕵️  OSINT", "desc": "Open-source intelligence gathering",
        "cats": ["documents", "sector", "secrets"],
        "packs": ["documents_sensitive", "email", "secrets"]},
    "custom": {"name": "⚙️  Custom", "desc": "Custom profile", "cats": [], "packs": []},
}


def _validate_profiles() -> None:
    """Fail fast at import time if a profile references an undefined pack."""
    for profile_name, profile in PROFILES.items():
        for pack_name in profile["packs"]:  # type: ignore[index]
            if pack_name not in KEYWORD_PACKS:
                raise ValueError(
                    f"Profile {profile_name!r} references undefined keyword "
                    f"pack {pack_name!r}"
                )
        for cat_name in profile["cats"]:  # type: ignore[index]
            if cat_name not in CATEGORIES:
                raise ValueError(
                    f"Profile {profile_name!r} references undefined category {cat_name!r}"
                )


_validate_profiles()
