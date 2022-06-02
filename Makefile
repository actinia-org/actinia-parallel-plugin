# Makefile to run setup.py

clean:
	python3 setup.py clean

docs:
	python3 setup.py docs

build:
	python3 setup.py build

install:
	python3 setup.py install

bdist:
	python3 setup.py bdist

dist:
	python3 setup.py dist

test:
	python3 setup.py test

unittest:
	python3 setup.py test --addopts "-m unittest"

devtest:
	python3 setup.py test --addopts "-m 'dev'"

integrationtest:
	python3 setup.py test --addopts "-m 'integrationtest'"
