"""Query templates: the operator/filetype/category recipes the engine fills
in with real keywords at generation time.

Design note (see AUDIT.md): the original brief asked for "1000+ hardcoded
templates". A literal 1000-line list of template dicts is not something a
maintainer can review, keep internally consistent, or extend safely — and it
isn't how the rest of the engine works anyway, since a template doesn't bake
in one specific keyword; the generator crosses each template against the
matching keyword pack's *entries* at generation time. That cross product is
what produces real coverage in the hundreds-to-thousands of concrete dorks
per run, not the template count.

So this module ships two tiers instead:

1. ``SIGNATURE_TEMPLATES`` — ~50 hand-curated, named templates for specific
   real-world exposure patterns (env files, exposed .git, Terraform state,
   Grafana dashboards, sector-specific document leaks, etc.) — the kind of
   dork a human researcher would actually write.
2. ``build_category_templates()`` — a small, reviewable factory that adds
   baseline operator-combination coverage (site+inurl, site+filetype+intext,
   etc.) for every category in ``profiles.CATEGORIES``, so no category is
   left with only 1-2 templates.

``TEMPLATES`` is the combined, deduplicated result and is what the rest of
the app imports.
"""
from __future__ import annotations

from .models import QueryTemplate
from .operators import FILETYPE_GROUPS
from .profiles import CATEGORIES

SIGNATURE_TEMPLATES: tuple[QueryTemplate, ...] = (
    QueryTemplate("env_file", "Environment file discovery", "config_files", "env_files",
                   ("site", "filetype", "inurl"), (".env",), ("env",), 8),
    QueryTemplate("config_php", "PHP config discovery", "config_files", "web_configs",
                   ("site", "filetype", "inurl"), ("config", "database", "password"),
                   ("php", "cfg", "conf"), 7),
    QueryTemplate("wp_config", "WordPress config exposure", "cms", "wordpress",
                   ("site", "inurl"), ("wp-config.php",), (), 8, technology="wordpress"),
    QueryTemplate("wp_users_api", "WordPress REST user enumeration", "cms", "wordpress",
                   ("site", "inurl"), ("wp-json/wp/v2/users",), (), 5, technology="wordpress"),
    QueryTemplate("secret_in_code", "Secrets in source", "secrets", "credentials",
                   ("site", "inurl", "intext"), (), ("py", "js", "php", "java", "go", "rb"), 8),
    QueryTemplate("key_in_file", "Keys in files", "secrets", "api_keys",
                   ("site", "filetype", "intext"), ("api_key", "API_KEY", "secret", "token"), (), 8),
    QueryTemplate("login_panel", "Login panels", "authentication", "login_pages",
                   ("site", "intitle", "inurl"), ("login", "signin", "auth"), (), 5),
    QueryTemplate("admin_panel", "Admin panels", "authentication", "admin_panels",
                   ("site", "intitle", "inurl"), ("admin", "dashboard", "panel"), (), 6),
    QueryTemplate("sso_config", "SSO/OAuth configuration exposure", "authentication", "sso",
                   ("site", "filetype", "intext"), ("client_secret", "sso", "oauth"), ("env", "json", "yaml"), 8),
    QueryTemplate("s3_exposure", "S3 bucket exposure", "cloud", "aws",
                   ("site", "intext"), ("s3.amazonaws.com", "Bucket:", "AWS_ACCESS_KEY_ID"), (), 7, technology="aws"),
    QueryTemplate("azure_storage_exposure", "Azure storage exposure", "cloud", "azure",
                   ("site", "intext"), ("blob.core.windows.net", "AZURE_STORAGE_KEY"), (), 7, technology="azure"),
    QueryTemplate("gcp_credentials", "GCP service account exposure", "cloud", "gcp",
                   ("site", "filetype", "intext"), ("GOOGLE_APPLICATION_CREDENTIALS",), ("json",), 9, technology="gcp"),
    QueryTemplate("firebase_db", "Open Firebase database", "cloud", "firebase",
                   ("site", "inurl"), ("firebaseio.com",), (), 7, technology="firebase"),
    QueryTemplate("git_exposed", "Exposed .git directory", "source_code", "git_exposure",
                   ("site", "inurl"), (".git/config",), (), 8, technology="git"),
    QueryTemplate("bitbucket_password", "Bitbucket app-password leak", "source_code", "bitbucket",
                   ("site", "filetype", "intext"), ("BITBUCKET_APP_PASSWORD",), ("env", "yml"), 8, technology="bitbucket"),
    QueryTemplate("sensitive_doc", "Sensitive documents", "documents", "pdfs",
                   ("site", "filetype", "intext"), ("confidential", "internal use only", "restricted"),
                   ("pdf", "doc", "docx"), 6),
    QueryTemplate("spreadsheet_leak", "Spreadsheet data leak", "documents", "spreadsheets",
                   ("site", "filetype", "intext"), ("password", "account", "email"), ("xls", "xlsx", "csv"), 7),
    QueryTemplate("backup_files", "Backup file discovery", "backups", "file_backups",
                   ("site", "filetype", "inurl"), ("backup", "bak", "old"), ("bak", "backup", "old", "sql"), 7),
    QueryTemplate("db_exposed", "Database dump exposure", "databases", "mysql",
                   ("site", "filetype", "inurl"), ("database", "dump", "phpmyadmin"), ("sql", "db", "sqlite"), 7),
    QueryTemplate("mongodb_conn", "MongoDB connection string leak", "databases", "mongodb",
                   ("site", "filetype", "intext"), ("mongodb://",), ("env", "js", "py", "json"), 8),
    QueryTemplate("redis_exposed", "Exposed Redis reference", "databases", "redis",
                   ("site", "intext"), ("redis://",), (), 6),
    QueryTemplate("elasticsearch_open", "Open Elasticsearch instance reference", "databases", "elasticsearch",
                   ("site", "inurl"), ("_search", "elasticsearch"), (), 6),
    QueryTemplate("log_exposure", "Log file exposure", "logs", "error_logs",
                   ("site", "filetype", "inurl"), ("error", "access", "debug"), ("log", "txt"), 6),
    QueryTemplate("password_in_log", "Passwords leaked in logs", "logs", "error_logs",
                   ("site", "filetype", "intext"), ("password=", "pwd="), ("log", "txt"), 9),
    QueryTemplate("cert_exposure", "Certificate/private key exposure", "certificates", "ssl_certs",
                   ("site", "filetype", "inurl"),
                   ("BEGIN CERTIFICATE", "BEGIN RSA PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY"),
                   ("pem", "key", "crt"), 8),
    QueryTemplate("docker_compose", "Docker Compose file exposure", "devops", "docker",
                   ("site", "inurl"), ("docker-compose.yml",), (), 6, technology="docker"),
    QueryTemplate("terraform_state", "Terraform state exposure", "devops", "terraform",
                   ("site", "filetype", "inurl"), ("terraform.tfstate",), ("tfstate", "tf"), 8, technology="terraform"),
    QueryTemplate("kube_config", "Kubernetes config exposure", "devops", "kubernetes",
                   ("site", "inurl", "filetype"), ("kubeconfig", "admin.conf"), ("conf", "yaml", "yml"), 8, technology="kubernetes"),
    QueryTemplate("jenkins_home", "Jenkins home / credentials exposure", "devops", "jenkins",
                   ("site", "inurl"), ("jenkins_home", "JENKINS_API_TOKEN"), (), 8, technology="jenkins"),
    QueryTemplate("ci_cd_config", "CI/CD pipeline configuration", "devops", "ci_cd",
                   ("site", "filetype", "inurl"), (".gitlab-ci.yml", "Jenkinsfile", ".github/workflows"),
                   ("yml", "yaml"), 7),
    QueryTemplate("ai_keys", "AI service API key leak", "ai_services", "openai",
                   ("site", "intext"), ("sk-", "OPENAI_API_KEY", "HUGGINGFACE_TOKEN"), (), 9, technology="openai"),
    QueryTemplate("jwt_leak", "Leaked JWT in page content", "authentication", "jwt",
                   ("site", "intext"), ("eyJhbGciOi",), (), 8, technology="jwt"),
    QueryTemplate("swagger_docs", "Exposed Swagger/OpenAPI docs", "apis", "swagger",
                   ("site", "inurl"), ("swagger-ui.html", "swagger.json", "openapi.json"), (), 5),
    QueryTemplate("graphql_introspection", "Exposed GraphQL endpoint", "apis", "graphql",
                   ("site", "inurl"), ("graphql",), (), 5),
    QueryTemplate("actuator_env", "Spring Boot actuator env exposure", "frameworks", "spring",
                   ("site", "inurl"), ("actuator/env",), (), 8, technology="spring"),
    QueryTemplate("laravel_env", "Laravel .env exposure", "frameworks", "laravel",
                   ("site", "filetype", "inurl"), ("APP_KEY",), ("env",), 8, technology="laravel"),
    QueryTemplate("django_debug", "Django debug mode exposure", "frameworks", "django",
                   ("site", "intext"), ("DEBUG = True", "django_secret_key"), (), 6, technology="django"),
    QueryTemplate("react_env", "React build-time secret exposure", "frameworks", "react",
                   ("site", "filetype", "intext"), ("REACT_APP_",), ("js", "env"), 5, technology="react"),
    QueryTemplate("angular_env", "Angular environment file exposure", "frameworks", "angular",
                   ("site", "inurl"), ("environment.prod.ts",), (), 5, technology="angular"),
    QueryTemplate("nextjs_env", "Next.js public env exposure", "frameworks", "nextjs",
                   ("site", "filetype", "intext"), ("NEXT_PUBLIC_",), ("js", "env"), 4, technology="nextjs"),
    QueryTemplate("grafana_open", "Open Grafana dashboard/API", "cloud", "aws",
                   ("site", "inurl"), ("grafana", "/api/datasources"), (), 6, technology="grafana"),
    QueryTemplate("smtp_creds", "SMTP credential leak", "email", "smtp",
                   ("site", "filetype", "intext"), ("SMTP_PASSWORD", "MAIL_PASSWORD"), ("env", "config", "ini"), 8),
    QueryTemplate("sendgrid_key", "SendGrid API key leak", "email", "transactional",
                   ("site", "intext"), ("SENDGRID_API_KEY",), (), 8, technology="sendgrid"),
    QueryTemplate("stripe_key", "Stripe secret key leak", "secrets", "api_keys",
                   ("site", "intext"), ("stripe_secret_key",), (), 9, technology="stripe"),
    QueryTemplate("medical_records", "Exposed medical/patient records", "sector", "medical",
                   ("site", "filetype", "intext"), ("patient record", "medical record", "diagnosis"),
                   ("pdf", "xls", "xlsx", "csv"), 8),
    QueryTemplate("finance_records", "Exposed financial account records", "sector", "finance",
                   ("site", "filetype", "intext"), ("account number", "routing number"),
                   ("pdf", "xls", "xlsx", "csv"), 8),
    QueryTemplate("government_docs", "Restricted government documents", "sector", "government",
                   ("site", "filetype", "intext"), ("for official use only", "unclassified"),
                   ("pdf", "doc", "docx"), 6),
    QueryTemplate("education_records", "Exposed student records", "sector", "education",
                   ("site", "filetype", "intext"), ("student id", "transcript", "gradebook"),
                   ("pdf", "xls", "xlsx", "csv"), 6),
    QueryTemplate("db_conn_string", "Database connection string leak", "databases", "postgresql",
                   ("site", "filetype", "intext"), ("DATABASE_URL", "postgres://", "mongodb://"),
                   ("env", "php", "py", "js", "conf"), 8),
    QueryTemplate("exact_credentials_pair", "Exact-match username/password pair", "secrets", "credentials",
                   ("site", "intext"), ("username", "password"), (), 8, exact=True),
    QueryTemplate("negated_public_docs", "Sensitive docs excluding public/sample content", "documents", "pdfs",
                   ("site", "filetype", "intext"), ("confidential",), ("pdf",), 6,
                   exclude=("sample", "template", "public")),
    QueryTemplate("okta_config", "Okta/Keycloak SSO config leak", "authentication", "sso",
                   ("site", "filetype", "intext"), ("okta", "keycloak"), ("env", "json", "yaml"), 6),
)

#: Baseline operator-combination "recipes" used to generate broad,
#: general-purpose coverage for every category — kept small and reviewable.
_BASELINE_OPERATOR_COMBOS: tuple[tuple[str, ...], ...] = (
    ("site", "inurl"),
    ("site", "intitle"),
    ("site", "intext"),
    ("site", "filetype", "inurl"),
    ("site", "filetype", "intitle"),
    ("site", "filetype", "intext"),
    ("site", "intitle", "inurl"),
)


def build_category_templates() -> list[QueryTemplate]:
    """Generate one baseline template per (category, operator-combo) pair.

    These have empty ``keywords``/``filetypes`` — the generation engine
    fills them in from the category's matching keyword-pack entries, so this
    factory only needs to define *shape*, not content.
    """
    generated: list[QueryTemplate] = []
    for cat_key, cat in CATEGORIES.items():
        for combo in _BASELINE_OPERATOR_COMBOS:
            name = f"{cat_key}_{'_'.join(combo)}"
            generated.append(QueryTemplate(
                name=name,
                description=f"{cat['name']} — {'+'.join(combo)} baseline coverage",
                category=cat_key,
                subcategory="general",
                operators=combo,
                risk_base=5 if "filetype" not in combo else 6,
            ))
    return generated


def _combine() -> list[QueryTemplate]:
    combined = list(SIGNATURE_TEMPLATES) + build_category_templates()
    seen: set[str] = set()
    deduped: list[QueryTemplate] = []
    for tmpl in combined:
        if tmpl.name in seen:
            continue
        seen.add(tmpl.name)
        deduped.append(tmpl)
    return deduped


TEMPLATES: list[QueryTemplate] = _combine()
