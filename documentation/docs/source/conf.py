"""Sphinx configuration for the LexNLP documentation."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT))

project = "LexNLP"
copyright = "2015–2026, ContraxSuite, LLC and LexPredict, LLC"
author = "ContraxSuite, LLC and LexPredict, LLC"

try:
    release = distribution_version("lexnlp")
except PackageNotFoundError:
    from lexnlp import __version__

    release = __version__
version = ".".join(release.split(".", maxsplit=2)[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
]

source_suffix = {".rst": "restructuredtext"}
root_doc = "index"
language = "en"

# ``api/`` is an obsolete sphinx-apidoc snapshot containing removed modules,
# tests, and one-page-per-constant output. Keep the existing extraction and NLP
# guides as the supported reference for this maintenance upgrade.
exclude_patterns = ["api/**", "build/**"]

pygments_style = "sphinx"
autodoc_member_order = "bysource"
autodoc_typehints = "description"

html_theme = "sphinx_rtd_theme"
html_logo = "_static/img/lexnlp_logo.png"
html_theme_options = {
    "logo_only": True,
    "style_nav_header_background": "#F4F6F9",
}
html_static_path = ["_static"]
html_show_sourcelink = False
html_css_files = ["css/custom_styles.css"]

htmlhelp_basename = "LexNLPdoc"

latex_documents = [
    (
        root_doc,
        "LexNLP.tex",
        "LexNLP Documentation",
        author,
        "manual",
    ),
]

man_pages = [
    (root_doc, "lexnlp", "LexNLP Documentation", [author], 1),
]

texinfo_documents = [
    (
        root_doc,
        "LexNLP",
        "LexNLP Documentation",
        author,
        "LexNLP",
        "Legal-text natural language processing and information extraction.",
        "Text Processing",
    ),
]
