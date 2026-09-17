#!/bin/bash
# 在 AutoDL 实例上初始化（镜像：PyTorch 2.5 / CUDA 12.4 / Python 3.12）。国内下权重走 hf-mirror。
set -e
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc; export HF_ENDPOINT=https://hf-mirror.com
echo 'export HF_HOME=/root/autodl-tmp/hf' >> ~/.bashrc; export HF_HOME=/root/autodl-tmp/hf; mkdir -p $HF_HOME
pip install -q -U pip
pip install -q "transformers>=4.45" accelerate timm tokenizers pillow numpy huggingface_hub
pip install -q "lerobot[smolvla,pi0]" || echo "lerobot 安装失败，π0/SmolVLA 按 lerobot 文档手装"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
echo "setup done"
