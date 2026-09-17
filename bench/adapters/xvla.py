# -*- coding: utf-8 -*-
"""xvla：需要该项目自己的运行时（见 README 的安装段），在租到的机器上按其 README 装好后补 load/make_inputs/step 三个函数。跑不通就如实记"未能复现"。"""
from . import Base
class Adapter(Base):
    def __init__(self, model_id): super().__init__(); self.model_id = model_id
    def load(self, precision): raise NotImplementedError("xvla 适配器待在 GPU 机上按项目 README 补齐")
    def make_inputs(self, image_res, seed): raise NotImplementedError
    def step(self, inputs): raise NotImplementedError
