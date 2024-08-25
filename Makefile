PROTO_FILES := $(shell find protobuf/ -type f -name '*.proto')
PROTO_PYTHON_DIR := src/python/lib/proto/
SRC_PYTHON_DIR := src/python
PROTO_PYTHON_FILES := $(patsubst %.proto,$(PROTO_PYTHON_DIR)%_pb2.py,$(PROTO_FILES))
PY_VENV := .venv/
TERRAFORM_INIT_DIR := terraform/.terraform
TERRAFORM_STATE_FILE := terraform/terraform.tfstate

.PHONY: bootstrap clean proto terraform

bootstrap: proto $(PY_VENV) terraform

clean:
	rm -rf cert/*.pem
	rm -rf cert/*.key
	rm -rf $(PROTO_PYTHON_DIR)/*_pb2.py
	rm -rf $(PY_VENV)
	rm -rf $(TERRAFORM_INIT_DIR)
	rm -rf $(TERRAFORM_STATE_FILE)
	rm -rf $(TERRAFORM_STATE_FILE).backup
	find . -name "__pycache__" | xargs rm -rf

proto: $(PROTO_PYTHON_DIR) $(PROTO_PYTHON_FILES)

terraform: $(TERRAFORM_STATE_FILE)

$(PROTO_PYTHON_DIR):
	mkdir -p $(PROTO_PYTHON_DIR)
	touch $(PROTO_PYTHON_DIR)/__init__.py

$(PROTO_PYTHON_FILES): $(PROTO_FILES)
	protoc -I=protobuf --python_out=$(PROTO_PYTHON_DIR) $^

$(PY_VENV):
	uv sync

$(TERRAFORM_STATE_FILE): $(TERRAFORM_INIT_DIR)
	cd terraform && terraform apply -auto-approve

$(TERRAFORM_INIT_DIR):
	cd terraform && terraform init -upgrade

lint:
	uvx ruff check $(SRC_PYTHON_DIR)
	uvx ruff format $(SRC_PYTHON_DIR)
