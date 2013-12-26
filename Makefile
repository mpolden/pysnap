all: lint test

test:
	nosetests

lint:
	flake8 --max-complexity=10 bin/*.py pysnap/*.py tests/*.py setup.py
