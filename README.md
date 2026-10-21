# MartinPdeS-docs

Shared Sphinx defaults for the MartinPdeS scientific Python repositories.

The package intentionally uses a flat layout. A project keeps its own
documentation content and assets, while this package supplies common Sphinx
extensions, theme defaults, responsive layout settings, and gallery behavior.
It also provides the shared author metadata, autodoc defaults, document
defaults, theme navigation, repository links, version switcher, and output
metadata used across the package family.

In a project's `docs/source/conf.py`:

```python
from martinpdes_docs import configure

globals().update(
    configure(
        project="PackLab",
        package="PackLab",
        repository="MartinPdeS/PackLab",
        logo="_static/logo.png",
        favicon="_static/favicon.png",
    )
)
```

Project-specific values can be assigned below this call to override any
shared default.

For a multi-section Sphinx-Gallery, pass the section names instead of
repeating the directory mappings:

```python
globals().update(
    configure(
        project="FlowCyPy",
        package="FlowCyPy",
        repository="MartinPdeS/FlowCyPy",
        gallery_sections=["tutorials", "studies", "validation"],
        gallery_default_thumb="_static/gallery-default.png",
    )
)
```

Use `gallery_options` for project-specific Sphinx-Gallery settings such as an
additional image scraper or an example error policy.

For packages with compiled extensions, set `prefer_installed_package=True` so
documentation builds import the installed wheel instead of the source
checkout.

The shared configuration also owns the common dark-mode context, CSS files,
autodoc defaults, and navigation metadata. Add only project-specific values in
`conf.py`, for example:

```python
globals().update(
    configure(
        project="SuPyMode",
        package="SuPyMode",
        repository="MartinPdeS/SuPyMode",
        extension_additions=["pyvista.ext.plot_directive"],
        html_css_files=["layout.css"],
        autodoc_default_options={"members": True},
        logo_text="",
    )
)
```

Use `include_gallery=False` for documentation sites without executable
examples. The default theme, context, CSS, and extension set then remain
centralized in this package.
