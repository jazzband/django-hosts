.PHONY: test

test:
	flake8 django_hosts
	py.test
