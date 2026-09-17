# -*- coding: utf-8 -*-
"""SmolVLA / π0 / π0.5（lerobot ≥0.6 策略）。lerobot 0.6 把分词、归一化放在预处理流水线里（make_pre_post_processors），
所以先按 config.input_features 造原始 batch → 过一次预处理（固定输入，只做一次，不计时）→ 计时只包含 predict_action_chunk。"""
from . import Base
REPOS = {"smolvla": "lerobot/smolvla_base", "pi0": "lerobot/pi0_base", "pi0.5": "lerobot/pi05_base"}
class Adapter(Base):
    def __init__(self, model_id): super().__init__(); self.model_id = model_id; self.hf_repo = REPOS[model_id]
    def load(self, precision):
        import torch
        from lerobot.policies.factory import make_pre_post_processors
        self.dtype = self._dtype(precision)
        if self.model_id == "smolvla":
            from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy as P
        elif self.model_id == "pi0":
            from lerobot.policies.pi0.modeling_pi0 import PI0Policy as P
        else:
            from lerobot.policies.pi05.modeling_pi05 import PI05Policy as P
        self.model = P.from_pretrained(self.hf_repo).to(self.device).eval()
        self.pre, self.post = make_pre_post_processors(self.model.config, pretrained_path=self.hf_repo)
        self.chunk = int(getattr(self.model.config, "n_action_steps", None) or getattr(self.model.config, "chunk_size", 50))
        self.revision = self._hf_revision(); return {"revision": self.revision, "repo": self.hf_repo, "vlm_layers": getattr(self.model.config, "num_vlm_layers", None)}
    def make_inputs(self, image_res, seed):
        import torch, numpy as np
        raw = {"task": self.INSTRUCTION}
        for k, f in self.model.config.input_features.items():
            shape = tuple(f.shape)
            if len(shape) == 3:   # 图像 (3,H,W)，用模型要求的分辩率
                img = self.make_image(shape[-1], seed).resize((shape[-1], shape[-2]))
                raw[k] = torch.from_numpy(np.asarray(img)).permute(2, 0, 1).float().div(255).unsqueeze(0)
            else:
                raw[k] = torch.zeros((1,) + shape)
        batch = self.pre(raw)
        return {k: (v.to(self.device) if hasattr(v, "to") else v) for k, v in batch.items()}
    def step(self, inputs):
        import torch
        with torch.inference_mode(): self.model.predict_action_chunk(inputs)
