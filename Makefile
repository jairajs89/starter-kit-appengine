all: debug

test:
	python -m unittest discover -v -t . -s test

debug:
	#TODO: use gsutil
	dev_appserver.py --host 0.0.0.0 .

deploy:
	#TODO: use gsutil
	make test && appcfg.py update --oauth2 .

.PHONY: test debug deploy
