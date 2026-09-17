#!/bin/bash
# 用法：bash run_matrix.sh rtx-4090   —— 依次跑第一批模型，失败的记录到 results/failed.txt 继续下一个
HW=${1:?hardware id}; cd "$(dirname "$0")"
for M in smolvla openvla spatialvla molmoact nora pi0 pi0.5 minivla vla-adapter; do
  echo "=== $M on $HW"; python3 bench.py --model $M --hardware $HW --precision bf16 || echo "$M $(date +%F)" >> results/failed.txt
done
