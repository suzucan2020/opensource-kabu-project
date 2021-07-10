NAME=python-kabu
VERSION=xxx
SHELL=/bin/bash

build:
	docker build -t $(NAME) .

run:
	docker run -it $(NAME) $(SHELL)

run2:
	docker run -it -v $(PWD):/mnt $(NAME) $(SHELL)
