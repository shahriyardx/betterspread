project = "betterspread"
copyright = "2026, Md Shahriyar Alam"
author = "Md Shahriyar Alam"
release = "1.0.5"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinxawesome_theme"
html_title = "betterspread"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#534AB7",
        "color-brand-content": "#534AB7",
    },
    "dark_css_variables": {
        "color-brand-primary": "#AFA9EC",
        "color-brand-content": "#AFA9EC",
    },
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
