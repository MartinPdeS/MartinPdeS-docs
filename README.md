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
