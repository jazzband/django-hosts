export DJANGO_SETTINGS_MODULE=django_hosts.test_settings

.PHONY: test

test:
	flake8 django_hosts --ignore=E124,E501,E127,E128
	py.test --cov django_hosts django_hosts
