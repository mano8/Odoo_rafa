#!/bin/bash
# docker_compose_up.sh
sudo docker-compose -f /opt/Odoo_rafa/docker-compose/odoo-prod/docker-compose.yml up -d --build
exit 0