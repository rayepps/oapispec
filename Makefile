
test:
	PYTHONPATH=`pwd` pytest --cov=swaggerf --cov-report term:skip-covered --cov-fail-under=100 --cov-report html tests/ -v

lint:
	pylint swaggerf
