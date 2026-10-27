from importlib.metadata import distribution
from pathlib import Path
import sys

import pytest

from martinpdes_docs import configure


def test_configuration_has_project_overrides():
    config = configure(project="Example", package="example", repository="MartinPdeS/Example")

    assert config["project"] == "Example"
    assert config["package"] == "example"
    assert config["html_logo"] == "_static/logo.svg"
    assert config["html_static_path"][0] == "_static"
    assert config["html_static_path"][1].endswith("martinpdes_docs/static")
    assert config["templates_path"] == ["_templates"]
    assert config["html_css_files"] == ["default.css", "martinpdes_layout.css"]
    assert config["html_context"]["doc_path"] == "docs/source"
    assert config["html_context"]["default_mode"] == "dark"
    assert config["epub_exclude_files"] == ["search.html"]
    assert config["autodoc_default_options"] == {
        "members": True,
        "exclude-members": "__annotations__",
        "members-order": "bysource",
        "undoc-members": False,
        "show-inheritance": True,
    }
    assert config["sphinx_gallery_conf"]["image_scrapers"] == ("matplotlib",)
    assert config["sphinx_gallery_conf"]["thumbnail_size"] == [600, 600]
    assert config["sphinx_gallery_conf"]["default_thumb_file"] is None
    assert config["sphinx_gallery_conf"]["reset_modules_order"] == "after"
    assert config["sphinx_gallery_conf"]["within_subsection_order"] == "FileNameSortKey"

    sections = configure(
        project="Example",
        package="example",
        gallery_sections=["tutorials", "validation"],
        gallery_default_thumb="_static/gallery-default.png",
    )
    assert sections["sphinx_gallery_conf"]["examples_dirs"] == [
        "../examples/tutorials",
        "../examples/validation",
    ]
    assert sections["sphinx_gallery_conf"]["gallery_dirs"] == [
        "gallery/tutorials",
        "gallery/validation",
    ]
    assert sections["sphinx_gallery_conf"]["default_thumb_file"] in {
        "_static/gallery-default.png",
        str(Path.cwd() / "docs" / "source" / "_static" / "gallery-default.png"),
    }

    raster = configure(
        project="Example",
        package="example",
        logo="../images/logo.png",
        favicon="_static/favicon.svg",
    )
    assert raster["sphinx_gallery_conf"]["default_thumb_file"].endswith("images/logo.png")
    assert "github_url" not in config["html_theme_options"]
    assert config["html_context"]["github_repo"] == "Example"


def test_custom_extensions_and_theme_options_are_preserved():
    config = configure(
        project="Example",
        package="example",
        extensions=["custom.extension"],
        html_theme_options={"announcement": "Hello"},
    )

    assert config["extensions"] == ["custom.extension"]

    defaults = configure(project="Example", package="example")
    assert "numpydoc" in defaults["extensions"]
    assert config["html_theme_options"]["announcement"] == "Hello"

    additions = configure(
        project="Example",
        package="example",
        extension_additions=["pyvista.ext.plot_directive"],
        html_css_files=["layout.css"],
        logo_text="",
        logo_alt_text="Example logo",
        autodoc_default_options={"members": True},
    )
    assert "pyvista.ext.plot_directive" in additions["extensions"]
    assert additions["html_css_files"][-1] == "layout.css"
    assert additions["html_theme_options"]["logo"] == {
        "text": "",
        "image": "_static/logo.svg",
        "alt_text": "Example logo",
    }
    assert additions["autodoc_default_options"]["members"] is True

    no_gallery = configure(
        project="Example",
        package="example",
        include_gallery=False,
    )
    assert "sphinx_gallery.gen_gallery" not in no_gallery["extensions"]
    assert "sphinx_gallery_conf" not in no_gallery


def test_gallery_options_override_shared_defaults():
    config = configure(
        project="Example",
        package="example",
        gallery_options={"image_scrapers": ("matplotlib", "pyvista")},
    )

    assert config["sphinx_gallery_conf"]["image_scrapers"] == ("matplotlib", "pyvista")


def test_gallery_thumbnail_paths_are_resolved_from_docs_source(tmp_path, monkeypatch):
    asset = tmp_path / "docs" / "source" / "_static" / "gallery-default.png"
    asset.parent.mkdir(parents=True)
    asset.write_bytes(b"png")
    monkeypatch.chdir(tmp_path)

    config = configure(
        project="Example",
        package="example",
        gallery_default_thumb="_static/gallery-default.png",
    )

    assert config["sphinx_gallery_conf"]["default_thumb_file"] == str(asset)


def test_version_can_be_resolved_from_the_environment(monkeypatch):
    monkeypatch.setenv("tag", "v2.3.4")

    config = configure(
        project="Example",
        package="example",
        repository="MartinPdeS/Example",
    )

    assert config["html_theme_options"]["switcher"]["version_match"] == "v2.3.4"


def test_auto_version_reads_package_file_without_importing_package(tmp_path, monkeypatch):
    package = tmp_path / "example_auto_version"
    package.mkdir()
    (package / "__init__.py").write_text("raise RuntimeError('package must not be imported')\n")
    (package / "_version.py").write_text('__version__ = version = "1.2.3"\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("tag", "v9.9.9")

    config = configure(
        project="Example", package="example_auto_version",
        repository="MartinPdeS/Example", version="auto",
    )

    assert config["version"] == config["release"] == "1.2.3"
    assert config["html_theme_options"]["switcher"]["version_match"] == "1.2.3"
    assert "example_auto_version" not in sys.modules


def test_auto_version_rejects_missing_or_invalid_version_file(tmp_path, monkeypatch):
    package = tmp_path / "example_invalid_version"
    package.mkdir()
    (package / "__init__.py").write_text("")
    monkeypatch.syspath_prepend(str(tmp_path))

    with pytest.raises(ValueError, match="Cannot find _version.py"):
        configure(project="Example", package="example_invalid_version", version="auto")
    (package / "_version.py").write_text("__version__ = None\n")
    with pytest.raises(ValueError, match="non-empty __version__"):
        configure(project="Example", package="example_invalid_version", version="auto")


def test_installed_package_can_be_preferred(monkeypatch):
    installed_site = str(distribution("MartinPdeS-docs").locate_file(""))
    monkeypatch.setattr(sys, "path", ["checkout", installed_site, "other"])

    configure(
        project="Example",
        package="MartinPdeS-docs",
        prefer_installed_package=True,
    )

    assert sys.path[0] == installed_site
    assert sys.path.count(installed_site) == 1
