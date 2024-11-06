# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys


# Function to read the version from version.py
def read_version():
    version_path = os.path.join(os.path.dirname(__file__), 'zacrostools', 'version.py')
    with open(version_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


version = read_version()

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ZacrosTools Documentation'
copyright = '2024, Hector Prats'
author = 'Hector Prats'
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser',
              'sphinx.ext.autodoc',
              'sphinx.ext.viewcode']  # add 'sphinx.ext.autosummary'? Chat GPT...

templates_path = ['_templates']
exclude_patterns = []

# Enable autosummary
# autosummary_generate = True  # Chat GPT ...

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
