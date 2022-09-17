from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent.absolute()

ABOUT_STYLESHEET_FILE = TEMPLATES_DIR.joinpath("about_stylesheet.css")

ABOUT_TEMPLATE_FILE = TEMPLATES_DIR.joinpath("about_template.jinja_html")


ARG_DOC_HTML_TEMPLATE_FILE = TEMPLATES_DIR.joinpath("arg_doc_html_template.jinja_html")

ARG_DOC_MARKDOWN_TEMPLATE_FILE = TEMPLATES_DIR.joinpath("arg_doc_markdown_template.jinja_md")
