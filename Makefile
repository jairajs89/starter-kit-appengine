all: debug

test:
	python -m unittest discover -v -t . -s test

debug:
	dev_appserver.py --host 0.0.0.0 .

deploy:
	make test && \
	gcloud app deploy app.yaml cron.yaml index.yaml --project starter-kit-4ppengine --quiet

.PHONY: test debug deploy
