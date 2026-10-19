"""Configurable defaults for the shared project documentation sites."""

from pathlib import Path


def configure(
    *,
    project: str,
    package: str,
    author: str = "Martin Poinsinet de Sivry-Houle",
    logo: str = "_static/logo.svg",
    favicon: str = "_static/favicon.svg",
    repository: str | None = None,
    extensions: list[str] | None = None,
    html_theme_options: dict | None = None,
) -> dict:
    """Return a Sphinx configuration dictionary for a project.

    In a project's ``conf.py`` use ``globals().update(configure(...))`` and
    keep project-specific settings below that call so they remain easy to
    override.
    """
    default_extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.intersphinx",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",
        "sphinx.ext.todo",
        "sphinx_design",
        "sphinx_gallery.gen_gallery",
    ]
    options = {
        "navigation_with_keys": True,
        "show_nav_level": 2,
        "navbar_align": "content",
        "show_toc_level": 2,
        "use_edit_page_button": bool(repository),
    }
    if repository:
        options["github_url"] = f"https://github.com/{repository}"
    if html_theme_options:
        options.update(html_theme_options)

    return {
        "project": project,
        "package": package,
        "author": author,
        "copyright": author,
        "extensions": extensions or default_extensions,
        "templates_path": ["_templates"],
        "exclude_patterns": ["_build", "Thumbs.db", ".DS_Store"],
        "html_theme": "pydata_sphinx_theme",
        "html_theme_options": options,
        "html_logo": logo,
        "html_favicon": favicon,
        "html_static_path": ["_static"],
        "autodoc_typehints": "description",
        "napoleon_google_docstring": False,
        "napoleon_numpy_docstring": True,
        "autosummary_generate": True,
        "sphinx_gallery_conf": {
            "examples_dirs": "../../examples",
            "gallery_dirs": "auto_examples",
            "filename_pattern": r"\.py$",
            "remove_config_comments": True,
        },
        "_martinpdes_package_root": str(Path(__file__).parent),
    }
