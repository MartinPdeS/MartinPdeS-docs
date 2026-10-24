PYTHON ?= python3

.PHONY: release-check
release-check:
	$(PYTHON) tools/check_release.py $(if $(VERSION),--version $(VERSION),)

RELEASE_KIND := $(filter major minor patch,$(MAKECMDGOALS))
.PHONY: release tag major minor patch
tag:
	$(PYTHON) tools/release_tag.py "$(VERSION)"
release:
	@test "$(words $(RELEASE_KIND))" -eq 1 || { echo "usage: make release [patch|minor|major]" >&2; exit 2; }
	@set -eu; release_tag="$$($(PYTHON) tools/next_release_version.py $(RELEASE_KIND))"; \
	$(PYTHON) tools/release_tag.py "$$release_tag"; \
	git push origin HEAD "refs/tags/$$release_tag"
major minor patch:
	@:
