# MartinPdeS-docs

Shared Sphinx defaults for the MartinPdeS scientific Python repositories.

The package intentionally uses a flat layout. A project keeps its own
documentation content and assets, while this package supplies common Sphinx
extensions, theme defaults, responsive layout settings, and gallery behavior.

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
