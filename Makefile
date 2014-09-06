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
