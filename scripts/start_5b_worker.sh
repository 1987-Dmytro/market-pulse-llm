#!/usr/bin/env bash
# The serverless worker's entrypoint, staged to /runpod-volume/start.sh (Phase 5b).
#
# A RunPod serverless worker runs one command and that command must be the handler loop.
# The image is the stock `runpod/pytorch` one — no registry credentials exist for this
# project and a custom image cannot be pushed — so everything this repo adds lives on the
# network volume: the checkout, a venv layered over the image's torch, and the weights.
#
# `set -euo pipefail` is load-bearing here. A worker whose venv is missing must die loudly
# at boot; one that limps on and answers nothing would burn the cold start and report a
# timeout, which reads like a model problem instead of a staging problem.
set -euo pipefail

export HF_HOME=/runpod-volume/hf
export HF_HUB_OFFLINE=1          # the weights are staged; a cold start must not re-download
export PYTHONPATH=/runpod-volume/repo/src
export TOKENIZERS_PARALLELISM=false

exec /runpod-volume/venv/bin/python -u /runpod-volume/repo/scripts/serve_handler.py
