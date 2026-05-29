# docker_offline/Makefile
#
# Single entry-point for vendoring everything needed for offline deployment.
#
#   make              → vendor wheels + images (prepare only, no load)
#   make load         → vendor wheels + images + load into local Docker
#   make wheels       → download Python wheels only
#   make images       → pull/build/save Docker images only
#   make clean        → remove all *.tar files and wheelhouse dirs

SUDO ?= sudo

.PHONY: all load wheels images clean

all: wheels images

load: wheels images
	@echo "Loading images into local Docker daemon…"
	$(SUDO) docker load -i python-3.11-slim.tar
	$(SUDO) docker load -i traefik_v3.4.0.tar
	$(SUDO) docker load -i postgres_13.21-alpine3.20.tar
	$(SUDO) docker load -i odoo_18.0.tar
	$(SUDO) docker load -i python-3.11-fat.tar
	$(SUDO) docker load -i prometheus_v3.4.0.tar
	$(SUDO) docker load -i grafana_12.0.1.tar

wheels:
	$(MAKE) -f Makefile.wheels prod
	$(MAKE) -f Makefile.wheels dev-all

images:
	$(MAKE) -f Makefile.prepare SUDO=$(SUDO)

clean:
	$(MAKE) -f Makefile.wheels clean
	rm -f *.tar
