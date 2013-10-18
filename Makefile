all: lint test

test:
	nosetests

lint:
	isort --skip= bin/*.py pysnap/*.py tests/*.py setup.py
	flake8 --max-complexity=10 bin/*.py pysnap/*.py tests/*.py setup.py
