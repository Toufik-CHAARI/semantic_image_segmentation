#!/bin/bash
set -e

echo "[INFO] Running in Lambda environment"

# Configure writable DVC config
mkdir -p /tmp/.dvc

echo "[INFO] Creating writable DVC configuration..."
cat << EOF > /tmp/.dvc/config
[core]
remote = myremote

['remote "myremote"']
url = s3://semantic-segmentation-models-1754924238
EOF

export DVC_CONFIG=/tmp/.dvc/config
export DVC_CACHE_DIR=/tmp/dvc-cache
export DVC_TEMP_DIR=/tmp/dvc-temp

mkdir -p "$DVC_CACHE_DIR" "$DVC_TEMP_DIR"

echo "[INFO] Pulling model with DVC..."
dvc pull --config "$DVC_CONFIG" --verbose
