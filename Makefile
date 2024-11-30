PROTO_DIR := packages/iot-proto/protobuf
PROTO_FILES := $(shell find $(PROTO_DIR) -type f -name '*.proto')
PROTO_PYTHON_DIR := packages/iot-proto/python/iot_proto
PROTO_PYTHON_FILES := $(patsubst %.proto,$(PROTO_PYTHON_DIR)%_pb2.py,$(PROTO_FILES))
PY_VENV := .venv/
SRC_PYTHON_DIR := src/iot_sample
TERRAFORM_INIT_DIR := terraform/.terraform
TERRAFORM_STATE_FILE := terraform/terraform.tfstate

.PHONY: bootstrap
bootstrap: proto $(PY_VENV) terraform

.PHONY: clean
clean:
	rm -rf cert/*.pem
	rm -rf cert/*.key
	rm -rf $(PROTO_PYTHON_DIR)/*_pb2.py
	rm -rf $(PY_VENV)
	rm -rf $(TERRAFORM_INIT_DIR)
	rm -rf $(TERRAFORM_STATE_FILE)
	rm -rf $(TERRAFORM_STATE_FILE).backup
	find . -name "__pycache__" | xargs rm -rf

.PHONY: proto
proto: $(PROTO_PYTHON_DIR) $(PROTO_PYTHON_FILES)

.PHONY: terraform
terraform: $(TERRAFORM_STATE_FILE)

$(PROTO_PYTHON_DIR):
	mkdir -p $(PROTO_PYTHON_DIR)
	touch $(PROTO_PYTHON_DIR)/__init__.py

$(PROTO_PYTHON_FILES): $(PROTO_FILES)
	protoc -I=$(PROTO_DIR) --python_out=$(PROTO_PYTHON_DIR) $^

uv.lock:
	uv sync --no-install-project

$(PY_VENV): export UV_FROZEN := true
$(PY_VENV): uv.lock
	uv sync --no-install-project

$(TERRAFORM_STATE_FILE): $(TERRAFORM_INIT_DIR)
	cd terraform && terraform apply -auto-approve

$(TERRAFORM_INIT_DIR):
	cd terraform && terraform init -upgrade

.PHONY: lint
lint:
	uv run ruff check $(SRC_PYTHON_DIR)
	uv run ruff format $(SRC_PYTHON_DIR)

.PHONY: release
release: export GIT_COMMIT_AUTHOR="$(shell git config user.name) <$(shell git config user.email)>"
release:
	uv run semantic-release version --no-commit --no-push --no-vcs-release ---skip-build --no-changelog
