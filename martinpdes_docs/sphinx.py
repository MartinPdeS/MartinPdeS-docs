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
    version: str = "latest",
    source_suffix: str = ".rst",
    master_doc: str = "index",
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
        "navbar_end": ["version-switcher", "navbar-icon-links"],
        "show_prev_next": False,
        "show_version_warning_banner": True,
        "footer_start": ["copyright"],
        "footer_end": ["sphinx-version", "theme-version"],
        "pygments_light_style": "default",
        "pygments_dark_style": "github-dark",
        "use_edit_page_button": bool(repository),
    }
    if repository:
        options["github_url"] = f"https://github.com/{repository}"
        options["icon_links"] = [
            {
                "name": "GitHub",
                "url": f"https://github.com/{repository}",
                "icon": "fa-brands fa-github",
            },
            {
                "name": "PyPI",
                "url": f"https://pypi.org/project/{package}/",
                "icon": "fa-solid fa-box",
            },
            {
                "name": "Anaconda",
                "url": f"https://anaconda.org/{repository.split('/')[0]}/{package}",
                "icon": "fa-brands fa-python",
            },
        ]
        options["switcher"] = {
            "json_url": f"https://raw.githubusercontent.com/{repository}/documentation_page/version_switcher.json",
            "version_match": version,
        }
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
        "autodoc_default_options": {
            "members": False,
            "members-order": "bysource",
            "undoc-members": False,
            "show-inheritance": True,
        },
        "napoleon_google_docstring": False,
        "napoleon_numpy_docstring": True,
        "autosectionlabel_prefix_document": True,
        "numpydoc_show_class_members": False,
        "add_module_names": False,
        "source_suffix": source_suffix,
        "master_doc": master_doc,
        "language": "en",
        "highlight_language": "python3",
        "exclude_trees": [],
        "pygments_style": "sphinx",
        "autosummary_generate": True,
        "htmlhelp_basename": f"{package}doc",
        "latex_elements": {},
        "latex_documents": [(master_doc, f"{package}.tex", f"{package} Documentation", author, "manual")],
        "man_pages": [(master_doc, package.lower(), f"{package} Documentation", [author], 1)],
        "texinfo_documents": [
            (master_doc, package, f"{package} Documentation", author, package,
             f"Documentation for {package}.", "Miscellaneous")
        ],
        "epub_title": project,
        "epub_exclude_files": ["search.html"],
        "sphinx_gallery_conf": {
            "examples_dirs": "../../examples",
            "gallery_dirs": "auto_examples",
            "filename_pattern": r"\.py$",
            "remove_config_comments": True,
        },
        "_martinpdes_package_root": str(Path(__file__).parent),
    }
