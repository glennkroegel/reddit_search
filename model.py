"""
created_by: Glenn Kroegel
Date: 17 August 2019

description: Wrapper for pretrained GPT language model

NOTE: I used this model mostly to save time. search.py can easily swap in/out other models specialized on this dataset (or unfreeze layers on this one).
"""

import torch
import torch.nn as nn
from pytorch_pretrained_bert import OpenAIGPTTokenizer, OpenAIGPTModel

class GPTModel(nn.Module):
    '''Wrapper for pretrained GPT model to get title vecs'''
    def __init__(self):
        super(GPTModel, self).__init__()
        self.mdl = OpenAIGPTModel.from_pretrained('openai-gpt')
        for param in self.mdl.parameters():
            param.requires_grad = False

    def forward(self, x):
        with torch.no_grad():
            x = self.mdl(x)
            return x