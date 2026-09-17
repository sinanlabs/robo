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
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo}
    def make_inputs(self, image_res, seed):
        img = self.make_image(image_res, seed)
        return self.processor(images=[img], text=self.INSTRUCTION, return_tensors="pt").to(self.device)
    def step(self, inputs):
        import torch
        with torch.inference_mode():
            out = self.model.predict_action(inputs); self.processor.decode_actions(out, unnorm_key="bridge_orig")
