all: lint test

test:
	python pysnap/tests.py

lint:
	flake8 --max-complexity=10 pysnap/*.py
