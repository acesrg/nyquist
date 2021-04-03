PEP8_CONFIG_FILE=.flake8
PEP8_DOCKER_IMAGE=pipelinecomponents/flake8
SPHINX_DOCKER_IMAGE=sphinxdoc/sphinx
DOCKER=docker run -it --rm

pep8:
	${DOCKER} -v $(PWD):/project -w /project ${PEP8_DOCKER_IMAGE} flake8 --config $(PEP8_CONFIG_FILE) .

docs:
	${DOCKER} -v $(PWD):/project -w /project/docs ${SPHINX_DOCKER_IMAGE}

.PHONY: pep8 docs
