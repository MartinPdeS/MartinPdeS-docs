"""Configurable defaults for the shared project documentation sites."""

import os
from collections.abc import Mapping, Sequence
import sys
from importlib.metadata import (
    PackageNotFoundError,
    distribution,
    version as distribution_version,
)
from pathlib import Path


def _raster_thumbnail_path(logo: str, favicon: str) -> str | None:
    """Choose a Sphinx-Gallery-compatible fallback thumbnail.

    Sphinx-Gallery requires a raster image for ``default_thumb_file``.  SVG
    files are valid theme logos and favicons, but are not accepted as gallery
    thumbnail sources by all supported Sphinx-Gallery versions.
    """
    raster_suffixes = {".png", ".jpg", ".jpeg", ".gif"}
    for candidate in (logo, favicon):
        if Path(candidate).suffix.lower() in raster_suffixes:
            return candidate
    return None


def _resolve_version(package: str, version: str | None) -> str:
    """Resolve the documentation version without importing the package."""
    if version is not None:
        return version

    environment_version = os.getenv("tag")
    if environment_version:
        return environment_version

    try:
        return distribution_version(package)
    except PackageNotFoundError:
        return "latest"


def _prefer_installed_package(package: str) -> None:
    """Put an installed distribution before the documentation checkout."""
    try:
        installed_site = str(distribution(package).locate_file(""))
    except PackageNotFoundError:
        return

    sys.path[:] = [entry for entry in sys.path if entry != installed_site]
    sys.path.insert(0, installed_site)


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
    sphinx_gallery_conf: dict | None = None,
    gallery_sections: Sequence[str] | None = None,
    gallery_default_thumb: str | None = None,
    gallery_options: Mapping[str, object] | None = None,
    prefer_installed_package: bool = False,
    version: str | None = None,
    source_suffix: str = ".rst",
    master_doc: str = "index",
) -> dict:
    """Return a Sphinx configuration dictionary for a project.

    In a project's ``conf.py`` use ``globals().update(configure(...))`` and
    keep project-specific settings below that call so they remain easy to
    override.  Pass ``gallery_sections`` when examples are split into named
    directories; use ``gallery_default_thumb`` for a project-specific raster
    fallback; use ``gallery_options`` for less common Sphinx-Gallery settings;
    and set ``prefer_installed_package`` for projects whose documentation must
    import a built wheel instead of the source checkout.
    """
    if prefer_installed_package:
        _prefer_installed_package(package)

    resolved_version = _resolve_version(package, version)

    default_extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.intersphinx",
        "sphinx.ext.mathjax",
        "sphinx.ext.napoleon",
        "sphinx.ext.autosectionlabel",
        "sphinx.ext.viewcode",
        "sphinx.ext.todo",
        "sphinx_design",
        "sphinx_gallery.gen_gallery",
    ]
    options = {
        "logo": {"text": project, "image": logo},
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
        owner, repo = repository.split("/", 1)
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
            "version_match": resolved_version,
        }

    html_context = {}
    if repository:
        owner, repo = repository.split("/", 1)
        ref_name = os.getenv("GITHUB_REF_NAME", "master")
        html_context.update(
            {
                "github_user": owner,
                "github_repo": repo,
                "github_version": ref_name,
            }
        )
    if html_theme_options:
        options.update(html_theme_options)

    gallery = {
        "examples_dirs": "../examples/",
        "gallery_dirs": "gallery/",
        "image_scrapers": ("matplotlib",),
        "ignore_pattern": "/__",
        "filename_pattern": r".*\.py",
        "plot_gallery": True,
        "thumbnail_size": [600, 600],
        "download_all_examples": False,
        "reset_modules_order": "after",
        "within_subsection_order": "FileNameSortKey",
        # Use the project's favicon for examples that do not create a figure.
        # The path is interpreted relative to the documentation source tree,
        # just like ``html_favicon``.
        "default_thumb_file": _raster_thumbnail_path(logo, favicon),
        "line_numbers": False,
        "remove_config_comments": True,
        "capture_repr": ("_repr_html_", "__repr__"),
        "nested_sections": True,
    }
    if gallery_sections:
        sections = list(gallery_sections)
        gallery["examples_dirs"] = [f"../examples/{section}" for section in sections]
        gallery["gallery_dirs"] = [f"gallery/{section}" for section in sections]
    if gallery_default_thumb is not None:
        gallery["default_thumb_file"] = gallery_default_thumb
    if gallery_options:
        gallery.update(gallery_options)
    if sphinx_gallery_conf:
        gallery.update(sphinx_gallery_conf)

    return {
        "project": project,
        "package": package,
        "author": author,
        "copyright": author,
        "extensions": extensions or default_extensions,
        "exclude_patterns": ["_build", "Thumbs.db", ".DS_Store"],
        "suppress_warnings": ["config.cache"],
        "html_theme": "pydata_sphinx_theme",
        "html_theme_options": options,
        "html_context": html_context,
        "html_logo": logo,
        "html_favicon": favicon,
        "html_static_path": ["_static", str(Path(__file__).parent / "static")],
        "templates_path": ["_templates"],
        "html_css_files": ["default.css", "martinpdes_layout.css"],
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
        "sphinx_gallery_conf": gallery,
        "_martinpdes_package_root": str(Path(__file__).parent),
    }
