# -*- coding: utf-8 -*-
"""OpenVLA-7B / MiniVLA / VLA-Adapter（OpenVLA 系，transformers 远程代码）。安装：pip install transformers timm tokenizers accelerate"""
from . import Base
REPOS = {"openvla": "openvla/openvla-7b", "minivla": "Stanford-ILIAD/minivla-vq-libero90-prismatic", "vla-adapter": "VLA-Adapter/LIBERO-Spatial"}
class Adapter(Base):
    chunk = 1
    def __init__(self, model_id): super().__init__(); self.model_id = model_id; self.hf_repo = REPOS[model_id]
    def load(self, precision):
        import torch; from transformers import AutoModelForVision2Seq, AutoProcessor
        self.dtype = self._dtype(precision)
        self.processor = AutoProcessor.from_pretrained(self.hf_repo, trust_remote_code=True)
        self.model = AutoModelForVision2Seq.from_pretrained(self.hf_repo, torch_dtype=self.dtype, low_cpu_mem_usage=True, trust_remote_code=True).to(self.device).eval()
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo}
    def make_inputs(self, image_res, seed):
        img = self.make_image(image_res, seed); prompt = "In: What action should the robot take to %s?\nOut:" % self.INSTRUCTION
        return self.processor(prompt, img).to(self.device, dtype=self.dtype)
    def step(self, inputs):
        import torch
        with torch.inference_mode(): self.model.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)
