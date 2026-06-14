# vim: ts=2 sw=2 sts=2 et :
# knobs only; shared targets live in $(KONFIG)/Makefile
KONFIG ?= ../konfig
APP    := nuff
MAIN   := nuff.py
EXT    := py
LANG   := python
SRC    := *.py
LINT   := ruff check nuff.py
TOOLS  := python3:run ruff:lint
PKG    := python3 gawk ruff neovim tmux

$(KONFIG)/Makefile:
	@test -f $@ || { echo "missing konfig: git clone http://tiny.cc/konfig $(KONFIG)"; exit 1; }
include $(KONFIG)/Makefile

test: ## smoke-test the three modules (needs ../optimiz)
	@python3 -B test_nuff.py && echo "ok nuff"

push2pypi: ## build + upload to PyPI (needs ~/.pypirc account token)
	@python3 -m build && python3 -m twine upload dist/*
	@rm -rf dist build *.egg-info
