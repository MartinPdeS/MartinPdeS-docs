from martinpdes_docs import configure


def test_configuration_has_project_overrides():
    config = configure(project="Example", package="example", repository="MartinPdeS/Example")

    assert config["project"] == "Example"
    assert config["package"] == "example"
    assert config["html_logo"] == "_static/logo.svg"
    assert config["html_static_path"] == ["_static"]
    assert config["templates_path"] == ["_templates"]
    assert config["html_css_files"] == ["default.css", "layout.css"]
    assert config["epub_exclude_files"] == ["search.html"]
    assert config["html_theme_options"]["github_url"].endswith("MartinPdeS/Example")


def test_custom_extensions_and_theme_options_are_preserved():
    config = configure(
        project="Example",
        package="example",
        extensions=["custom.extension"],
        html_theme_options={"announcement": "Hello"},
    )

    assert config["extensions"] == ["custom.extension"]
    assert config["html_theme_options"]["announcement"] == "Hello"
