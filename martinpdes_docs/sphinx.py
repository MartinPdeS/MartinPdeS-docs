"""Configurable defaults for the shared project documentation sites."""

import os
import runpy
from collections.abc import Mapping, Sequence
from importlib.util import find_spec
import sys
from importlib.metadata import (
    PackageNotFoundError,
    distribution,
    version as distribution_version,
)
from pathlib import Path
import warnings


def _deep_merge(base: dict, override: Mapping) -> dict:
    """Merge nested mappings without mutating either input mapping."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(merged.get(key), Mapping) and isinstance(value, Mapping):
            merged[key] = _deep_merge(dict(merged[key]), value)
        else:
            merged[key] = value
    return merged


def _parse_repository(repository: str) -> tuple[str, str]:
    """Validate and split a ``owner/repository`` GitHub identifier."""
    parts = repository.split("/")
    if len(parts) != 2 or not all(parts) or any(part.strip() != part for part in parts):
        raise ValueError("repository must be a GitHub identifier in the form 'owner/name'.")
    return parts[0], parts[1]


def _raster_thumbnail_path(logo: str, favicon: str, docs_root: Path | None = None) -> str | None:
    """Choose a Sphinx-Gallery-compatible fallback thumbnail.

    Sphinx-Gallery requires a raster image for ``default_thumb_file``.  SVG
    files are valid theme logos and favicons, but are not accepted as gallery
    thumbnail sources by all supported Sphinx-Gallery versions.
    """
    raster_suffixes = {".png", ".jpg", ".jpeg", ".gif"}
    for candidate in (logo, favicon):
        if Path(candidate).suffix.lower() in raster_suffixes:
            return _resolve_doc_asset(candidate, docs_root)
    return None


def _resolve_doc_asset(path: str, docs_root: Path | None = None) -> str:
    """Resolve a documentation asset relative to common Sphinx build roots."""
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)

    roots = tuple(root for root in (docs_root, Path.cwd(), Path.cwd() / "docs" / "source") if root is not None)
    for root in roots:
        resolved = root / candidate
        if resolved.is_file():
            return str(resolved)
    return path


def _resolve_version(package: str, version: str | None) -> str:
    """Resolve the documentation version without importing the package."""
    if version == "auto":
        spec = find_spec(package)
        locations = spec.submodule_search_locations if spec is not None else None
        if locations is None:
            raise ValueError(f"Cannot find package {package!r} to read its _version.py.")
        for location in locations:
            version_file = Path(location) / "_version.py"
            if version_file.is_file():
                resolved = runpy.run_path(str(version_file)).get("__version__")
                if not isinstance(resolved, str) or not resolved:
                    raise ValueError(f"{version_file} must define a non-empty __version__ string.")
                return resolved
        raise ValueError(f"Cannot find _version.py in package {package!r}.")
    if version is not None:
        return version

    environment_version = os.getenv("tag")
    if environment_version:
        return environment_version

    try:
        return distribution_version(package)
    except PackageNotFoundError:
        warnings.warn(
            f"Could not resolve an installed distribution for {package!r}; using 'latest'. "
            "Pass version= explicitly or use version='auto' for published documentation.",
            RuntimeWarning,
            stacklevel=2,
        )
        return "latest"


def _prefer_installed_package(package: str) -> None:
    """Put an installed distribution before the documentation checkout."""
    try:
        installed_site = str(distribution(package).locate_file(""))
    except PackageNotFoundError:
        warnings.warn(
            f"prefer_installed_package=True but distribution {package!r} is not installed; "
            "documentation imports may resolve to the source checkout.",
            RuntimeWarning,
            stacklevel=2,
        )
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
    extensions: Sequence[str] | None = None,
    extension_additions: Sequence[str] | None = None,
    html_theme_options: dict | None = None,
    logo_text: str | None = None,
    logo_alt_text: str | None = None,
    html_context: Mapping[str, object] | None = None,
    html_css_files: Sequence[str] | None = None,
    autodoc_default_options: Mapping[str, object] | None = None,
    sphinx_gallery_conf: dict | None = None,
    gallery_sections: Sequence[str] | None = None,
    gallery_default_thumb: str | None = None,
    gallery_options: Mapping[str, object] | None = None,
    prefer_installed_package: bool = False,
    include_gallery: bool = True,
    version: str | None = None,
    docs_root: str | Path | None = None,
    profile: str = "default",
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
    import a built wheel instead of the source checkout. Set ``version="auto"``
    to read ``__version__`` from the importable package's ``_version.py`` and
    use it for both Sphinx version fields and the version switcher.
    """
    if profile not in {"default", "scientific-gallery", "minimal"}:
        raise ValueError("profile must be one of 'default', 'scientific-gallery', or 'minimal'.")
    if profile == "minimal":
        include_gallery = False

    resolved_docs_root = Path(docs_root).resolve() if docs_root is not None else None

    if prefer_installed_package:
        _prefer_installed_package(package)

    resolved_version = _resolve_version(package, version)

    options = {
        "logo": {"text": project if logo_text is None else logo_text, "image": logo},
        "navigation_with_keys": True,
        "show_nav_level": 1,
        "navbar_align": "content",
        "show_toc_level": 2,
        "navbar_end": ["version-switcher", "theme-switcher", "navbar-icon-links"],
        "show_prev_next": True,
        "show_version_warning_banner": True,
        "footer_start": ["copyright"],
        "footer_end": [],
        "pygments_light_style": "default",
        "pygments_dark_style": "github-dark",
        "use_edit_page_button": bool(repository),
    }
    if logo_alt_text is not None:
        options["logo"]["alt_text"] = logo_alt_text
    if repository:
        owner, repo = _parse_repository(repository)
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
                "url": f"https://anaconda.org/{owner}/{package}",
                "icon": "fa-brands fa-python",
            },
        ]
        options["switcher"] = {
            "json_url": f"https://raw.githubusercontent.com/{repository}/documentation_page/version_switcher.json",
            "version_match": resolved_version,
        }

    context = {
        "doc_path": "docs/source",
        "default_mode": "dark",
    }
    if repository:
        owner, repo = _parse_repository(repository)
        ref_name = os.getenv("GITHUB_REF_NAME", "master")
        context.update(
            {
                "github_user": owner,
                "github_repo": repo,
                "github_version": ref_name,
            }
        )
    if html_context:
        context.update(html_context)
    if html_theme_options:
        options = _deep_merge(options, html_theme_options)

    default_extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.mathjax",
        "sphinx.ext.napoleon",
        "numpydoc",
        "sphinx.ext.autosectionlabel",
        "sphinx.ext.viewcode",
        "sphinx.ext.todo",
        "sphinx_design",
    ]
    if include_gallery:
        default_extensions.append("sphinx_gallery.gen_gallery")
    if extensions is None:
        configured_extensions = default_extensions + list(extension_additions or ())
    else:
        configured_extensions = list(extensions)

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
        "default_thumb_file": _raster_thumbnail_path(logo, favicon, resolved_docs_root),
        "line_numbers": False,
        "remove_config_comments": True,
        "capture_repr": ("_repr_html_", "__repr__"),
        "nested_sections": True,
    }
    if not include_gallery:
        gallery = None
    elif gallery_sections:
        sections = list(gallery_sections)
        gallery["examples_dirs"] = [f"../examples/{section}" for section in sections]
        gallery["gallery_dirs"] = [f"gallery/{section}" for section in sections]
    if gallery is not None:
        if gallery_default_thumb is not None:
            gallery["default_thumb_file"] = _resolve_doc_asset(gallery_default_thumb, resolved_docs_root)
        if gallery_options:
            gallery.update(gallery_options)
        if sphinx_gallery_conf:
            gallery.update(sphinx_gallery_conf)

    css_files = ["default.css", "martinpdes_layout.css"]
    css_files.extend(html_css_files or ())
    autodoc_options = {
        "members": True,
        "exclude-members": "__annotations__",
        "members-order": "bysource",
        "undoc-members": False,
        "show-inheritance": True,
    }
    autodoc_options.update(autodoc_default_options or {})

    configuration = {
        "project": project,
        "package": package,
        "version": resolved_version,
        "release": resolved_version,
        "author": author,
        "copyright": author,
        "extensions": configured_extensions,
        "exclude_patterns": ["_build", "Thumbs.db", ".DS_Store"],
        "suppress_warnings": ["config.cache"],
        "html_theme": "pydata_sphinx_theme",
        "html_theme_options": options,
        "html_context": context,
        "html_logo": logo,
        "html_favicon": favicon,
        "html_static_path": ["_static", str(Path(__file__).parent / "static")],
        "templates_path": ["_templates"],
        "html_css_files": css_files,
        "autodoc_typehints": "description",
        "autodoc_default_options": autodoc_options,
        "napoleon_google_docstring": False,
        "napoleon_numpy_docstring": True,
        "napoleon_use_ivar": True,
        "show_authors": True,
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
        "texinfo_documents": [(master_doc, package, f"{package} Documentation", author, package, f"Documentation for {package}.", "Miscellaneous")],
        "epub_title": project,
        "epub_exclude_files": ["search.html"],
        "_martinpdes_package_root": str(Path(__file__).parent),
    }
    if gallery is not None:
        configuration["sphinx_gallery_conf"] = gallery
    return configuration
