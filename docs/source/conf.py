# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = 'ZacrosTools Documentation'
copyright = '2024, Hector Prats'
author = 'Hector Prats'

from zacrostools.version import __version__

release = __version__

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Add the following lines to set the logo
html_logo = "../images/logo.png"  # Path relative to the _static directory

# Optional: Customize theme options (if needed)
html_theme_options = {
    #'logo_only': True,  # Uncomment to display only the logo without the project name
    #'display_version': True,  # Uncomment to hide the version in the sidebar
    # Add more theme options here if desired
}
