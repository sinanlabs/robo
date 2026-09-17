# -*- coding: utf-8 -*-
"""MolmoAct-7B（transformers 远程代码，生成式输出动作 token）。"""
from . import Base
class Adapter(Base):
    chunk = 1
    def __init__(self, model_id): super().__init__(); self.model_id = model_id; self.hf_repo = "allenai/MolmoAct-7B-D-0812"
    def load(self, precision):
        import torch; from transformers import AutoModelForImageTextToText, AutoProcessor
        self.dtype = self._dtype(precision)
        self.processor = AutoProcessor.from_pretrained(self.hf_repo, trust_remote_code=True)
        self.model = AutoModelForImageTextToText.from_pretrained(self.hf_repo, torch_dtype=self.dtype, trust_remote_code=True).to(self.device).eval()
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo}
    def make_inputs(self, image_res, seed):
        img = self.make_image(image_res, seed)
        text = self.processor.apply_chat_template([{"role": "user", "content": [dict(type="text", text="The task is %s. What is the action that the robot should take?" % self.INSTRUCTION)]}], tokenize=False, add_generation_prompt=True)
        return self.processor(images=[img], text=text, return_tensors="pt").to(self.device)
    def step(self, inputs):
        import torch
        with torch.inference_mode(): self.model.generate(**inputs, max_new_tokens=64, do_sample=False)
