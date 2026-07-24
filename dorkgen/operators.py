"""The registry of Google search operators DorkGEN knows how to combine.

``ext:`` is kept as a genuinely distinct operator from ``filetype:`` (the
original code accepted both but always rendered ``filetype:`` — see
AUDIT.md). Some search engines/tools only recognize one or the other, so
templates that ask for ``ext`` now actually render ``ext:``.
"""
from __future__ import annotations

from .models import FileType, Operator

OPERATORS: dict[str, Operator] = {
    "site": Operator("site", "Restrict results to a specific domain"),
    "filetype": Operator("filetype", "Restrict results to a file extension", quote_multiword=False),
    "ext": Operator("ext", "Alias of filetype used by some search engines", quote_multiword=False),
    "intitle": Operator("intitle", "Keyword must appear in the page title"),
    "allintitle": Operator("allintitle", "All keywords must appear in the page title"),
    "inurl": Operator("inurl", "Keyword must appear in the URL"),
    "allinurl": Operator("allinurl", "All keywords must appear in the URL"),
    "intext": Operator("intext", "Keyword must appear in the page body"),
    "allintext": Operator("allintext", "All keywords must appear in the page body"),
    "cache": Operator("cache", "Show the cached version of a page", quote_multiword=False),
    "related": Operator("related", "Find sites related to a domain", quote_multiword=False),
    "info": Operator("info", "Show summary info Google has about a page", quote_multiword=False),
    "define": Operator("define", "Define a term"),
}

#: Operators that take a keyword/phrase (as opposed to a domain or filetype).
KEYWORD_OPERATORS: tuple[str, ...] = (
    "intitle", "allintitle", "inurl", "allinurl", "intext", "allintext",
)

#: Operators that take a filetype extension.
FILETYPE_OPERATORS: tuple[str, ...] = ("filetype", "ext")

#: Operators that take a domain.
DOMAIN_OPERATORS: tuple[str, ...] = ("site", "cache", "related", "info")

FILETYPES: dict[str, FileType] = {
    "pdf": FileType("pdf", "document", 4), "doc": FileType("doc", "document", 5),
    "docx": FileType("docx", "document", 5), "xls": FileType("xls", "spreadsheet", 6),
    "xlsx": FileType("xlsx", "spreadsheet", 6), "ppt": FileType("ppt", "presentation", 5),
    "pptx": FileType("pptx", "presentation", 5), "csv": FileType("csv", "data", 5),
    "json": FileType("json", "data", 6), "xml": FileType("xml", "data", 5),
    "sql": FileType("sql", "database", 8), "db": FileType("db", "database", 7),
    "sqlite": FileType("sqlite", "database", 7), "mdb": FileType("mdb", "database", 8),
    "env": FileType("env", "config", 9), "cfg": FileType("cfg", "config", 6),
    "conf": FileType("conf", "config", 6), "config": FileType("config", "config", 6),
    "ini": FileType("ini", "config", 5), "yaml": FileType("yaml", "config", 6),
    "yml": FileType("yml", "config", 6), "toml": FileType("toml", "config", 6),
    "pem": FileType("pem", "certificate", 9), "key": FileType("key", "certificate", 9),
    "crt": FileType("crt", "certificate", 8), "p12": FileType("p12", "certificate", 8),
    "log": FileType("log", "log", 6), "txt": FileType("txt", "document", 3),
    "bak": FileType("bak", "backup", 8), "backup": FileType("backup", "backup", 8),
    "old": FileType("old", "backup", 7), "php": FileType("php", "code", 5),
    "asp": FileType("asp", "code", 5), "aspx": FileType("aspx", "code", 5),
    "jsp": FileType("jsp", "code", 5), "py": FileType("py", "code", 5),
    "js": FileType("js", "code", 5), "java": FileType("java", "code", 5),
    "go": FileType("go", "code", 5), "rb": FileType("rb", "code", 5),
    "sh": FileType("sh", "script", 6), "ps1": FileType("ps1", "script", 7),
    "tf": FileType("tf", "devops", 6), "tfstate": FileType("tfstate", "devops", 8),
    "dockerfile": FileType("dockerfile", "devops", 5),
}

#: Curated filetype groups used by the template factory to avoid a template
#: exploding across every one of the 30+ known extensions.
FILETYPE_GROUPS: dict[str, tuple[str, ...]] = {
    "config": ("env", "cfg", "conf", "config", "ini", "yaml", "yml", "toml"),
    "database": ("sql", "db", "sqlite", "mdb"),
    "certificate": ("pem", "key", "crt", "p12"),
    "backup": ("bak", "backup", "old", "sql", "db"),
    "document": ("pdf", "doc", "docx", "txt"),
    "spreadsheet": ("xls", "xlsx", "csv"),
    "log": ("log", "txt"),
    "code": ("py", "js", "php", "java", "go", "rb"),
    "devops": ("tf", "tfstate", "yml", "yaml"),
}
