PEP8_CONFIG_FILE=.flake8

PEP8_DOCKER_IMAGE=pipelinecomponents/flake8
SPHINX_DOCKER_IMAGE=sphinxdoc/sphinx
PYTHON_DOCKER_IMAGE=python:3.8.7-slim-buster

DEV_CONTAINER=control_lab_client_dev

DOCKER=docker run -it --rm

pep8:
	${DOCKER} -v $(PWD):/project -w /project ${PEP8_DOCKER_IMAGE} flake8 --config $(PEP8_CONFIG_FILE) .

docs:
	${DOCKER} -v $(PWD):/project -w /project/docs ${SPHINX_DOCKER_IMAGE}

build:
	docker run -dit -v $(PWD):/project -w /project --name ${DEV_CONTAINER} ${PYTHON_DOCKER_IMAGE} bash
	docker exec ${DEV_CONTAINER} pip3 install .

try: build
	- docker exec -it ${DEV_CONTAINER} python3
	docker stop ${DEV_CONTAINER}
	docker rm ${DEV_CONTAINER}

test: build
	- docker exec -it ${DEV_CONTAINER} python3 -m unittest discover -v tests/
	docker stop ${DEV_CONTAINER}
	docker rm ${DEV_CONTAINER}

stop:
	docker stop ${DEV_CONTAINER}

clean:
	docker rm ${DEV_CONTAINER}

.PHONY: pep8 docs build try test stop clean
