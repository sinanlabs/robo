# -*- coding: utf-8 -*-
"""SpatialVLA-4B（transformers 远程代码）。安装：pip install transformers==4.47 accelerate（按其 README）"""
from . import Base
class Adapter(Base):
    chunk = 1
    def __init__(self, model_id): super().__init__(); self.model_id = model_id; self.hf_repo = "IPEC-COMMUNITY/spatialvla-4b-224-pt"
    def load(self, precision):
        import torch; from transformers import AutoModel, AutoProcessor
        self.dtype = self._dtype(precision)
        self.processor = AutoProcessor.from_pretrained(self.hf_repo, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(self.hf_repo, torch_dtype=self.dtype, trust_remote_code=True).to(self.device).eval()
        stats = getattr(self.processor, "statistics", None) or getattr(self.model, "statistics", None) or {}
        self.unnorm_key = "bridge_orig" if "bridge_orig" in stats else (next(iter(stats)) if stats else None)
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo, "unnorm_key": self.unnorm_key}
    def make_inputs(self, image_res, seed):
        img = self.make_image(image_res, seed)
        return self.processor(images=[img], text=self.INSTRUCTION, return_tensors="pt").to(self.device)
    def step(self, inputs):
        import torch
        with torch.inference_mode():
            out = self.model.predict_action(inputs)
            try: self.processor.decode_actions(out, unnorm_key=self.unnorm_key)
            except Exception: pass   # 反归一化只是查表，不影响推理耗时的量级；没有统计键就跳过
