BASE_TAG ?= 3.8.18-slim-bullseye
IMAGE_TAG ?= 3.8

PYTHON ?= $(shell which python3)
DOCKER ?= $(shell which docker)

BUNDLE_PATH := bundle
TEMPLATE_PATH := template

BACKEND_PATH := $(TEMPLATE_PATH)/src/backend
BACKEND_SOURCES := $(wildcard $(BACKEND_PATH)/*.py)

prerequisites:
	$(PYTHON) -m pip install jinja2-cli yapf

format: $(BACKEND_SOURCES) | prerequisites
	$(PYTHON) -m yapf -i $^ --style "{based_on_style: google, column_limit: 400, indent_width: 4}"

image: $(TEMPLATE_PATH)/Dockerfile | format $(BACKEND_SOURCES) $(FRONTEND_SOURCES)
	$(DOCKER) build $(TEMPLATE_PATH) -f $^ -t webhood/$(IMAGE_TAG)

clean:
	$(RM) $(TEMPLATE_PATH)/Dockerfile

test: image
	$(DOCKER) run --rm -p 80:80 -p 443:443 webhood/$(IMAGE_TAG)

test-bash: image
	$(DOCKER) run --rm -p 80:80 -p 443:443 -it webhood/$(IMAGE_TAG) bash

bundle: image
	$(DOCKER) compose --project-directory $(BUNDLE_PATH) up --build

$(TEMPLATE_PATH)/Dockerfile: $(TEMPLATE_PATH)/Dockerfile.template | prerequisites
	$(PYTHON) -m jinja2cli.cli $^ -DTAG=$(BASE_TAG) > $@