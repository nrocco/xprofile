prefix=/usr

.PHONY: install
install:
	python setup.py install
	install -Dm644 zsh/completions "$(prefix)/share/zsh/site-functions/_xprofile"


.PHONY: uninstall
uninstall:
	rm -f "$(prefix)/share/zsh/site-functions/_xprofile"


.PHONY: clean
clean:
	rm -rf .tox *.egg dist build .coverage
	find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print

.PHONY: publish
publish:
	python setup.py register
	python setup.py sdist upload

man:
	mkdir -p build/man
	rst2man.py docs/man/xprofile.1.rst build/man/xprofile.1
	rst2man.py docs/man/xprofilerc.5.rst build/man/xprofilerc.5

docs:
	mkdir -p build
	rst2html.py CHANGELOG.rst build/CHANGELOG.html
	rst2html.py README.rst build/README.html
	rst2html.py docs/man/xprofile.1.rst build/xprofile.1.html
	rst2html.py docs/man/xprofilerc.5.rst build/xprofilerc.5.html

.PHONY: test
test:
	python setup.py test
