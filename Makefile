prefix=/usr

.PHONY: install
install:
	install -Dm755 xprofile "$(prefix)/bin/xprofile"
