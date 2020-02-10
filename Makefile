
.PHONY: test
test:
	python -m pytest --version
	PYTHONPATH=`pwd` python -m pytest --cov=oapispec --cov-report term:skip-covered --cov-fail-under=100 --cov-report html tests/ -vv

.PHONY: lint
lint:
	pylint --version
	pylint oapispec

.PHONY: create-dist
create-dist:
	python3 setup.py sdist

.PHONY: upload-dist
upload-dist:
	TWINE_USERNAME="__token__" \
  TWINE_PASSWORD="${token}" \
	twine upload dist/*

.PHONY: test-upload-dist
test-upload-dist:
	TWINE_USERNAME="__token__" \
  TWINE_PASSWORD="${token}" \
  TWINE_REPOSITORY_URL="https://test.pypi.org/legacy" \
  twine upload dist/*

.PHONY: check
check: lint test
	@echo "🎉 Check passed 👍"

PYVERSIONS := "3.6 3.7 3.8"
PYPATH := /Library/Frameworks/Python.framework/Versions

.PHONY: venv
venv:
	@if test $(findstring ${version}, $(PYVERSIONS)) ; \
    then \
      echo "Creating virtual environment for python ${version}"; \
      $(PYPATH)/${version}/bin/python3 -m venv venv; \
    else \
      echo "Unsupported python version (${version}). oapispec supports $(PYVERSIONS)"; \
    fi

.PHONY: install
install:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt
	pip install -r requirements.test.txt

.PHONY: setup-swagger-cli
setup-swagger-cli:
	npm install swagger-cli # <- used for testing the generated spec is valid in end_to_end tests
	rm package-lock.json
