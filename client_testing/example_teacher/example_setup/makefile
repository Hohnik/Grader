.PHONY: build push

all: push

build:
	docker build --no-cache -t hohniki/teacher_test:latest .

push: build
	docker push hohniki/teacher_test:latest

