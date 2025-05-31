#!/bin/sh

# This one has been used at RunPod instance ("pod") with CUDA, Python, and PyTorch preinstalled.
# Adjust it for your particular cloud GPU provider(s).

apt update
apt install mc tmux 7zip lm-sensors

python -m pip install -U pip
pip install -U accelerate coqui-tts datasets soundfile transformers

mkdir /workspace/huggingface_cache
export HF_HOME=/workspace/huggingface_cache

mkdir /workspace/coquitts_cache
export TTS_HOME=/workspace/coquitts_cache
