NAME=python-kabu
VERSION=xxx
SHELL=/bin/bash

build:
	docker build -t $(NAME) .

run:
	docker run -it $(NAME) $(SHELL)
