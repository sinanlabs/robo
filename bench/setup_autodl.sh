#!/bin/bash
# AutoDL 初始化 v2：pypi 用华为云镜像（实测 8 MB/s，阿里/清华在该机房只有 KB 级）；权重走 hf-mirror；
# 不同模型的 transformers 版本互相冲突，按组建 venv：openvla(4.40.1) / spatialvla(4.47.0) / qwen(4.57) 共享系统 torch 2.5.1；lerobot 独立完整 venv（它要 torch>=2.7）。
set -u
export PATH=/root/miniconda3/bin:$PATH
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple >/dev/null; pip config set global.trusted-host repo.huaweicloud.com >/dev/null
grep -q HF_ENDPOINT ~/.bashrc || { echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc; echo 'export HF_HOME=/root/autodl-tmp/hf' >> ~/.bashrc; }
export HF_ENDPOINT=https://hf-mirror.com HF_HOME=/root/autodl-tmp/hf HF_HUB_DISABLE_XET=1; mkdir -p $HF_HOME /root/envs
pip install -q -U "huggingface_hub[cli]" pillow numpy 2>&1 | grep -v WARNING
mk() { # name, packages...
  local n=$1; shift
  [ -d /root/envs/$n ] || python -m venv --system-site-packages /root/envs/$n
  /root/envs/$n/bin/pip install -q "$@" 2>&1 | grep -v WARNING; echo "env $n ready"
}
mk openvla "transformers==4.40.1" "timm==0.9.10" "tokenizers==0.19.1" accelerate &
mk spatialvla "transformers==4.47.0" accelerate &
mk qwen "transformers==4.57.1" accelerate qwen-vl-utils &
( [ -d /root/envs/lerobot ] || python -m venv /root/envs/lerobot; /root/envs/lerobot/bin/pip install -q -U pip >/dev/null; /root/envs/lerobot/bin/pip install -q "lerobot[smolvla]" 2>&1 | grep -v WARNING; echo "env lerobot ready" ) &
# 权重预下载（并行，走 hf-mirror）
for r in lerobot/smolvla_base openvla/openvla-7b IPEC-COMMUNITY/spatialvla-4b-224-pt; do huggingface-cli download $r > /dev/null 2>&1 && echo "weights $r ready" & done
wait
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "setup done"
