PROTO_DIR := packages/iot-proto/protobuf
PROTO_FILES := $(shell find $(PROTO_DIR) -type f -name '*.proto')
PROTO_PYTHON_DIR := packages/iot-proto/python/iot_proto
PROTO_PYTHON_FILES := $(patsubst %.proto,$(PROTO_PYTHON_DIR)%_pb2.py,$(PROTO_FILES))
PY_VENV := .venv/
SRC_PYTHON_DIR := src/iot_sample
IAC_INIT_DIR := iac/.terraform
IAC_STATE_FILE := iac/terraform.tfstate
IAC_LOCK_FILE := iac/.terraform.lock.hcl
IAC_BINARY := tofu

.PHONY: bootstrap
bootstrap: proto $(PY_VENV) iac
	uv run pre-commit install

.PHONY: clean
clean:
	rm -rf cert/*.pem
	rm -rf cert/*.key
	rm -rf $(PROTO_PYTHON_DIR)/*_pb2.py
	rm -rf $(PY_VENV)
	rm -rf $(IAC_INIT_DIR)
	rm -rf $(IAC_STATE_FILE)
	rm -rf $(IAC_STATE_FILE).backup
	rm -rf $(IAC_LOCK_FILE)
	find . -name "__pycache__" | xargs rm -rf

.PHONY: proto
proto: $(PROTO_PYTHON_DIR) $(PROTO_PYTHON_FILES)

.PHONY: iac
iac: $(IAC_STATE_FILE)

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

$(IAC_STATE_FILE): $(IAC_INIT_DIR)
	cd iac && $(IAC_BINARY) apply -auto-approve

$(IAC_INIT_DIR):
	cd iac && $(IAC_BINARY) init -upgrade

.PHONY: lint
lint:
	uv run pre-commit run --all-files

.PHONY: typing
typing:
	uv run ty check

.PHONY: release
release: export GIT_COMMIT_AUTHOR="$(shell git config user.name) <$(shell git config user.email)>"
release:
	uv run semantic-release version --no-commit --no-push --no-vcs-release ---skip-build --no-changelog

.PHONY: test
test:
	uv run pytest src/python_tests/ --cov=src/iot_sample/iot --cov-report=term-missing
