all: lint test

test:
	python pysnap/tests.py
	python3 pysnap/tests.py

lint:
	isort pysnap/*.py
	flake8 --max-complexity=10 pysnap/*.py
