# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'gidapptools'
copyright = '2022, brocaprogs'
author = 'brocaprogs'

# The full version, including alpha/beta/rc tags
release = '0.3.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinxcontrib.mermaid',
              "sphinxcontrib.fulltoc",
              "sphinx.ext.githubpages",
              "sphinx.ext.autodoc",
              'sphinx_copybutton',
              "sphinx_design",
              'sphinx.ext.autosectionlabel']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


html_css_files = ["css/extra_style.css"]


import json
from pathlib import Path
import jinja2
THIS_FILE_DIR = Path(__file__).parent.absolute()


def create_attributions():
    atttributions_data_file = THIS_FILE_DIR.joinpath("_data", "attributions.json")

    with atttributions_data_file.open("r", encoding='utf-8', errors='ignore') as f:
        data = json.load(f)

    atttributions_template_file = THIS_FILE_DIR.joinpath("_templates", "attributions.jinja_rst")

    jinja_env = jinja2.Environment(loader=jinja2.BaseLoader())
    template = jinja_env.from_string(atttributions_template_file.read_text(encoding='utf-8', errors='ignore'))

    output_file = THIS_FILE_DIR.joinpath("attributions.rst")

    output_file.write_text(template.render(data=data), encoding='utf-8', errors='ignore')


create_attributions()
