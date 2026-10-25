PYTHON ?= python3

.PHONY: release-check
release-check:
	$(PYTHON) -m martinpdes_maintenance.cli check $(if $(VERSION),--version $(VERSION),)

RELEASE_KIND := $(filter major minor patch,$(MAKECMDGOALS))
.PHONY: release tag major minor patch
tag:
	$(PYTHON) -m martinpdes_maintenance.cli tag "$(VERSION)"
release:
	@test "$(words $(RELEASE_KIND))" -eq 1 || { echo "usage: make release [patch|minor|major]" >&2; exit 2; }
	@set -eu; release_tag="$$($(PYTHON) -m martinpdes_maintenance.cli next $(RELEASE_KIND))"; \
	$(PYTHON) -m martinpdes_maintenance.cli tag "$$release_tag"; \
	git push origin HEAD "refs/tags/$$release_tag"
major minor patch:
	@:
