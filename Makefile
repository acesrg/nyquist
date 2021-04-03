PEP8_CONFIG_FILE=.flake8
PEP8_DOCKER_IMAGE=pipelinecomponents/flake8
DOCKER=docker run -it --rm

pep8:
	${DOCKER} -v $(PWD):/project -w /project ${PEP8_DOCKER_IMAGE} flake8 --config $(PEP8_CONFIG_FILE) .
