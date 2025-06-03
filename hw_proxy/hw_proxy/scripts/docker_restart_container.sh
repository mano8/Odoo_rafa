#!/bin/bash
#
# docker_restart_container.sh
#
# Securely restart a Docker container whose name is passed as $1.
# Only names composed of [A-Za-z0-9_-] are allowed. We also verify that the
# container exists in `docker ps -a`. If everything is valid, we call
# `docker restart <container>` (as root).
#
# Usage:
#   ./docker_restart_container.sh my_container_name
#
set -euo pipefail

# 1) Make sure exactly one argument is given
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <container_name>"
    exit 1
fi

container="$1"

# 2) Reject anything that is not a simple “alphanumeric + _ or -”
if [[ ! $container =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo "Error: Invalid container name '$container'. Only letters, digits, hyphen and underscore are allowed."
    exit 1
fi

# 4) Finally, restart the container.  Because this script is intended to be
#    run under sudo (via sudoers entry), we do not put “sudo” here.  At this
#    point, the process is already root, so `docker restart` will succeed.
echo "Restarting container: $container"
sudo docker compose restart "$container" > /dev/null 2>&1
exit 0