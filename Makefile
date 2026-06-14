# vim: ts=2 sw=2 sts=2 et :
# knobs only; shared targets live in $(KONFIG)/Makefile
KONFIG ?= ../konfig
APP    := gape
MAIN   := gape.py
EXT    := py
LANG   := python
SRC    := *.py
LINT   := ruff check gape.py data.py dist.py
TOOLS  := python3:run ruff:lint
PKG    := python3 gawk ruff neovim tmux

$(KONFIG)/Makefile:
	@test -f $@ || { echo "missing konfig: git clone http://tiny.cc/konfig $(KONFIG)"; exit 1; }
include $(KONFIG)/Makefile

test: ## smoke-test the three modules (needs ../optimiz)
	@python3 -B test_gape.py && echo "ok gape"
