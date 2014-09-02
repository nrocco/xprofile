prefix=/usr

.PHONY: install
install:
	install -Dm755 xprofile "$(prefix)/bin/xprofile"
	install -Dm644 zsh/completions "$(prefix)/share/zsh/site-functions/_xprofile"

.PHONY: uninstall
uninstall:
	rm -f "$(prefix)/bin/xprofile"
	rm -f "$(prefix)/share/zsh/site-functions/_xprofile"
