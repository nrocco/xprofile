prefix=/usr

.PHONY: install
install:
	python setup.py install
	install -Dm644 zsh/completions "$(prefix)/share/zsh/site-functions/_xprofile"

.PHONY: uninstall
uninstall:
	rm -f "$(prefix)/share/zsh/site-functions/_xprofile"
