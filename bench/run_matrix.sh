#!/bin/bash
# 用法：bash run_matrix.sh rtx-4090 [model ...]  —— 按模型选对应 venv 跑分；失败记 results/failed.txt；跑完清该模型权重（数据盘 50 GB）
HW=${1:?hardware id}; shift; cd "$(dirname "$0")"
export HF_ENDPOINT=https://hf-mirror.com HF_HOME=/root/autodl-tmp/hf
declare -A ENV=( [openvla]=openvla [minivla]=openvla [vla-adapter]=openvla [spatialvla]=spatialvla [molmoact]=qwen [nora]=qwen [smolvla]=lerobot [pi0]=lerobot [pi0.5]=lerobot )
MODELS=${@:-smolvla openvla spatialvla molmoact nora pi0 pi0.5 minivla vla-adapter}
for M in $MODELS; do
  PY=/root/envs/${ENV[$M]}/bin/python; echo "=== $M on $HW ($PY) $(date +%H:%M)"
  $PY bench.py --model $M --hardware $HW --precision bf16 || echo "$M $(date +%F)" >> results/failed.txt
  rm -rf $HF_HOME/hub/models--* 2>/dev/null
done
echo "matrix done"
