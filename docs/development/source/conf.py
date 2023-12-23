# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Z21 Client'
copyright = '2023, Frank Herbrand'
author = 'Frank Herbrand'
release = '0.0.1'

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
# #################################################################################
#
#
# ####>>> see: https://stackoverflow.com/questions/2701998/automatically-document-all-modules-recursively-with-sphinx-autodoc
#
# Damit klappt es. Benötigt wird der Ordner _templates mit seinem Inhalt (ist
# standardmäßig leer!)

sys.path.insert(0, os.path.abspath('../../..'))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]
autosummary_generate = True
autosummary_ignore_module_all = False
autosummary_imported_members = False

autoclass_content = 'both' # use class- and __init__-Docstring
autodoc_member_order = 'bysource' # sorting of documentated components
autodoc_typehints = 'both' # type hints in signature and description
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'private-members': True,
    'special-members': True,
    'undoc-members': True,
    'exclude-members': '__weakref__, __dict__'
}


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '__pycache__']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
#html_theme = 'alabaster'
#html_static_path = ['_static']
