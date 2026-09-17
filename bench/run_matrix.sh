#!/bin/bash
# 用法：bash run_matrix.sh rtx-4090 [model ...]  —— 按模型选 venv 逐个跑分；失败记 results/failed.txt；跑完只删该模型自己的权重（数据盘 50 GB）
HW=${1:?hardware id}; shift; cd "$(dirname "$0")"
export HF_ENDPOINT=https://hf-mirror.com HF_HOME=/root/autodl-tmp/hf HF_HUB_DISABLE_XET=1
declare -A ENV=( [openvla]=openvla [minivla]=openvla [vla-adapter]=openvla [spatialvla]=spatialvla [molmoact]=qwen [nora]=qwen [smolvla]=lerobot [pi0]=lerobot [pi0.5]=lerobot )
declare -A REPO=( [openvla]="openvla--openvla-7b" [minivla]="Stanford-ILIAD--minivla-vq-libero90-prismatic" [vla-adapter]="VLA-Adapter--LIBERO-Spatial" [spatialvla]="IPEC-COMMUNITY--spatialvla-4b-224-pt" [molmoact]="allenai--MolmoAct-7B-D-0812" [nora]="declare-lab--nora" [smolvla]="lerobot--smolvla_base" [pi0]="lerobot--pi0_base" [pi0.5]="lerobot--pi05_base" )
MODELS=${@:-smolvla openvla spatialvla molmoact nora pi0 pi0.5 minivla vla-adapter}
for M in $MODELS; do
  PY=/root/envs/${ENV[$M]}/bin/python; echo "=== $M on $HW ($PY) $(date +%H:%M)"
  if $PY bench.py --model $M --hardware $HW --precision bf16 > logs_$M.log 2>&1; then tail -1 logs_$M.log; rm -rf $HF_HOME/hub/models--${REPO[$M]} 2>/dev/null   # 成功才删权重，失败留着好重试
  else echo "$M $(date +%F) FAILED" | tee -a results/failed.txt; grep -v -E "Fetching|Loading|Warning|warn" logs_$M.log | tail -3; fi
  df -h $HF_HOME | tail -1 | awk '{print "disk used", $3, "of", $2}'
done
echo "matrix done"
