ROUTERS_IMG  ?= ecommerce-flow-routers:dev
# Path to the deliveryhero/asya repo (relative to this Makefile location)
ASYA_ROOT    ?= ../../deliveryhero/asya
FLOW_OUT     ?= build/ecommerce_flow_compiled
CLUSTER_NAME ?= asya-e2e-sqs-s3
NAMESPACE    ?= example-ecom

.PHONY: flow-compile flow-build flow-restart flow-all

flow-compile:
	@echo "[+] Compiling flow to $(FLOW_OUT)"
	PYTHONPATH=.:$(ASYA_ROOT)/src/asya-cli \
	  python3.13 $(ASYA_ROOT)/src/asya-cli/asya_cli/flow_cli.py \
	    compile flows/ecommerce_flow.py \
	    --output-dir "$(FLOW_OUT)" \
	    --overwrite --plot --plot-width 50

flow-build: flow-compile
	@echo "[+] Staging runtime script into build/"
	mkdir -p build
	cp $(ASYA_ROOT)/src/asya-runtime/asya_runtime.py build/asya_runtime.py
	@echo "[+] Building routers image $(ROUTERS_IMG)"
	docker build -f Dockerfile.ecommerce-runtime -t $(ROUTERS_IMG) .
	@echo "[+] Loading image into kind cluster $(CLUSTER_NAME)"
	kind load docker-image $(ROUTERS_IMG) --name "$(CLUSTER_NAME)"

flow-restart:
	@echo "[+] Restarting start-ecommerce-flow deployment in namespace $(NAMESPACE)"
	kubectl -n $(NAMESPACE) rollout restart deployment/start-ecommerce-flow
	kubectl -n $(NAMESPACE) wait --for=condition=available --timeout=180s deployment/start-ecommerce-flow

flow-all: flow-build flow-restart
	@echo "[+] Flow compile/build/load/restart complete"
