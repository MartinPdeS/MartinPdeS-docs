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
    assert config["epub_exclude_files"] == ["search.html"]
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
    assert sections["sphinx_gallery_conf"]["default_thumb_file"] == (
        "_static/gallery-default.png"
    )

    raster = configure(
        project="Example",
        package="example",
        logo="../images/logo.png",
        favicon="_static/favicon.svg",
    )
    assert raster["sphinx_gallery_conf"]["default_thumb_file"] == "../images/logo.png"
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
    assert config["html_theme_options"]["announcement"] == "Hello"


def test_gallery_options_override_shared_defaults():
    config = configure(
        project="Example",
        package="example",
        gallery_options={"image_scrapers": ("matplotlib", "pyvista")},
    )

    assert config["sphinx_gallery_conf"]["image_scrapers"] == ("matplotlib", "pyvista")


def test_version_can_be_resolved_from_the_environment(monkeypatch):
    monkeypatch.setenv("tag", "v2.3.4")

    config = configure(
        project="Example",
        package="example",
        repository="MartinPdeS/Example",
    )

    assert config["html_theme_options"]["switcher"]["version_match"] == "v2.3.4"
