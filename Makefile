prefix ?= /usr

.PHONY: install
install:
	python setup.py install --prefix="$(prefix)" --root="$(DESTDIR)" --optimize=1
	install -Dm644 zsh/completions "$(DESTDIR)$(prefix)/share/zsh/site-functions/_xprofile"
	install -Dm644 xprofile.1      "$(DESTDIR)$(prefix)/share/man/man1/xprofile.1"
	install -Dm644 xprofilerc.5    "$(DESTDIR)$(prefix)/share/man/man5/xprofilerc.5"


.PHONY: uninstall
uninstall:
	rm -f "$(DESTDIR)$(prefix)/share/zsh/site-functions/_xprofile"
	rm -f "$(DESTDIR)$(prefix)/share/man/man1/xprofile.1"
	rm -f "$(DESTDIR)$(prefix)/share/man/man5/xprofilerc.5"


.PHONY: clean
clean:
	rm -rf .tox *.egg dist build .coverage
	find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print


xprofile.1: docs/man/xprofile.1.rst
	rst2man.py $< $@


xprofilerc.5: docs/man/xprofilerc.5.rst
	rst2man.py $< $@


man: xprofile.1 xprofilerc.5


docs:
	mkdir -p build
	rst2html.py CHANGELOG.rst build/CHANGELOG.html
	rst2html.py README.rst build/README.html
	rst2html.py docs/man/xprofile.1.rst build/xprofile.1.html
	rst2html.py docs/man/xprofilerc.5.rst build/xprofilerc.5.html


.PHONY: test
test:
	python setup.py test


.PHONY: publish
publish:
	python setup.py register
	python setup.py sdist upload
