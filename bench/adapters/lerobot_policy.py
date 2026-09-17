# -*- coding: utf-8 -*-
"""SmolVLA / π0 / π0.5（lerobot 策略）。安装：pip install "lerobot[smolvla,pi0]" 或按 lerobot 文档；权重 lerobot/smolvla_base、lerobot/pi0_base、lerobot/pi05_base。"""
from . import Base
REPOS = {"smolvla": "lerobot/smolvla_base", "pi0": "lerobot/pi0_base", "pi0.5": "lerobot/pi05_base"}
class Adapter(Base):
    def __init__(self, model_id): super().__init__(); self.model_id = model_id; self.hf_repo = REPOS[model_id]
    def load(self, precision):
        import torch
        self.dtype = self._dtype(precision)
        if self.model_id == "smolvla":
            from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy as P
        elif self.model_id == "pi0":
            from lerobot.policies.pi0.modeling_pi0 import PI0Policy as P
        else:
            from lerobot.policies.pi05.modeling_pi05 import PI05Policy as P
        self.model = P.from_pretrained(self.hf_repo).to(self.device).eval()
        self.chunk = int(getattr(self.model.config, "n_action_steps", getattr(self.model.config, "chunk_size", 50)))
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo}
    def make_inputs(self, image_res, seed):
        import torch, numpy as np
        img = torch.from_numpy(np.asarray(self.make_image(image_res, seed))).permute(2, 0, 1).float().div(255).unsqueeze(0).to(self.device)
        cfg = self.model.config; feats = getattr(cfg, "input_features", {}) or {}
        batch = {"task": [self.INSTRUCTION]}
        for k, f in feats.items():
            shape = tuple(f.shape) if hasattr(f, "shape") else None
            if "image" in k or (shape and len(shape) == 3): batch[k] = img
            elif shape: batch[k] = torch.zeros((1,) + shape, device=self.device)
        return batch
    def step(self, inputs):
        import torch
        with torch.inference_mode():
            if hasattr(self.model, "predict_action_chunk"): self.model.predict_action_chunk(inputs)
            else: self.model.reset(); self.model.select_action(inputs)
