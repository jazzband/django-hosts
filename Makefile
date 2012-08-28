export DJANGO_SETTINGS_MODULE=django_hosts.test_settings

.PHONY: test

test:
	flake8 django_hosts --ignore=E501
	coverage run --branch --source=django_hosts `which django-admin.py` test django_hosts
	coverage report --omit=*test*
