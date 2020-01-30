
.PHONY: test
test:
	PYTHONPATH=`pwd` python -m pytest --cov=oapispec --cov-report term:skip-covered --cov-fail-under=100 --cov-report html tests/ -vv

.PHONY: lint
lint:
	pylint oapispec

.PHONY: create-dist
create-dist:
	python setup.py sdist

.PHONY: upload-dist
upload-dist:
	twine upload dist/*

.PHONY: check
check: lint test
	@echo "🎉 Check passed 👍"

.PHONY: venv
venv:
	# If your on windows you need to figure out where python 3.8 is installed and use that path
	# If you don't have this version installed - install it
	/Library/Frameworks/Python.framework/Versions/3.8/bin/python3 -m venv venv

.PHONY: install
install:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt
	pip install -r requirements.test.txt
	npm install -g swagger-cli # <- used for testing the generated spec is valid in end_to_end tests
