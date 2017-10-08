all: server

install:
	pip install --upgrade --user --quiet --requirement requirements.dev.txt

xlib:
	pip install --upgrade --no-deps --requirement requirements.xlib.txt -t xlib

server:
	dev_appserver.py --host 0.0.0.0 .

lint:
	flake8 . --ignore=E121,E123,E126,E226,E24,E704,E501,E402 --exclude=xlib/*

test:
	make lint && \
	python -m unittest discover -v -t . -s test

deploy:
	make test && \
	gcloud app deploy app.yaml cron.yaml index.yaml --quiet --project starter-kit-4ppengine

.PHONY: install xlib server lint test deploy
