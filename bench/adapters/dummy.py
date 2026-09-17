# -*- coding: utf-8 -*-
"""假模型：验证跑分流程与输出格式，不需要 GPU。"""
import time
from . import Base
class Adapter(Base):
    name = "dummy"; chunk = 8
    def __init__(self, model_id): super().__init__(); self.model_id = model_id
    def load(self, precision): self.dtype = precision; return {"revision": "dummy", "params_b": 0}
    def make_inputs(self, image_res, seed): return {"image": self.make_image(image_res, seed), "text": self.INSTRUCTION}
    def step(self, inputs): time.sleep(0.002)
    def sync(self): pass
    def vram_peak_gb(self): return 0.0
