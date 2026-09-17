# -*- coding: utf-8 -*-
"""模型适配器：每个模型实现 load / make_inputs / step / sync / vram_peak_gb / action_chunk。
同一套固定输入：确定性合成 RGB 图（seed 固定）、同一句指令、零状态向量。只测推理开销，不评价动作质量。"""
import importlib

class Base:
    name = "base"; chunk = 1; hf_repo = None
    def __init__(self): self.model = None; self.device = "cuda"; self.dtype = None; self.revision = None
    def _dtype(self, precision):
        import torch; return {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[precision]
    def _hf_revision(self):
        try:
            from huggingface_hub import HfApi; return HfApi().model_info(self.hf_repo).sha[:12]
        except Exception: return None
    def make_image(self, res, seed):
        import numpy as np; from PIL import Image
        rng = np.random.default_rng(seed); yy, xx = np.mgrid[0:res, 0:res]
        arr = np.stack([(xx * 255 // res), (yy * 255 // res), ((xx + yy) * 255 // (2 * res))], -1).astype("uint8")
        arr = (arr * 0.7 + rng.integers(0, 80, arr.shape)).clip(0, 255).astype("uint8")
        return Image.fromarray(arr)
    INSTRUCTION = "pick up the red cup and place it on the plate"
    def sync(self):
        try:
            import torch
            if torch.cuda.is_available(): torch.cuda.synchronize()
        except Exception: pass
    def vram_peak_gb(self):
        try:
            import torch
            return round(torch.cuda.max_memory_allocated() / 2**30, 2) if torch.cuda.is_available() else None
        except Exception: return None
    def action_chunk(self): return self.chunk
    def load(self, precision): raise NotImplementedError
    def make_inputs(self, image_res, seed): raise NotImplementedError
    def step(self, inputs): raise NotImplementedError

ADAPTERS = {"dummy": "dummy", "openvla": "openvla", "smolvla": "lerobot_policy", "pi0": "lerobot_policy", "pi0.5": "lerobot_policy", "spatialvla": "spatialvla", "molmoact": "molmoact", "nora": "nora",
            "gr00t-n1.7": "gr00t", "gr00t-n1.6-3b": "gr00t", "rdt-1b": "rdt", "cogact": "cogact", "univla": "univla", "x-vla": "xvla", "octo": "octo", "minivla": "openvla", "vla-adapter": "openvla"}

def get_adapter(model_id):
    mod = importlib.import_module("adapters." + ADAPTERS[model_id]); a = mod.Adapter(model_id); return a
