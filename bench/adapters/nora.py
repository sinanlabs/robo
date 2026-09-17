# -*- coding: utf-8 -*-
"""NORA（Qwen2.5-VL 3B 底座，动作为离散 token）。"""
from . import Base
class Adapter(Base):
    chunk = 1
    def __init__(self, model_id): super().__init__(); self.model_id = model_id; self.hf_repo = "declare-lab/nora"
    def load(self, precision):
        import torch; from transformers import AutoModelForImageTextToText, AutoProcessor
        self.dtype = self._dtype(precision)
        self.processor = AutoProcessor.from_pretrained(self.hf_repo, trust_remote_code=True)
        self.model = AutoModelForImageTextToText.from_pretrained(self.hf_repo, torch_dtype=self.dtype, trust_remote_code=True).to(self.device).eval()
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo}
    def make_inputs(self, image_res, seed):
        img = self.make_image(image_res, seed)
        text = self.processor.apply_chat_template([{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": self.INSTRUCTION}]}], tokenize=False, add_generation_prompt=True)
        return self.processor(images=[img], text=text, return_tensors="pt").to(self.device)
    def step(self, inputs):
        import torch
        with torch.inference_mode(): self.model.generate(**inputs, max_new_tokens=16, do_sample=False)
