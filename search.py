"""
created_by: Glenn Kroegel
Date: 17 August 2019

description: 
"""

import pandas as pd
import numpy as np
import json
import torch
from elasticsearch import Elasticsearch
from pytorch_pretrained_bert import OpenAIGPTTokenizer, OpenAIGPTModel
from tqdm import tqdm
from model import GPTModel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN

from multiprocessing.pool import Pool

INDEX = "data"
HOST = "127.0.0.1"

class ImageSearcher():
    def __init__(self, host=HOST, port=9200, timeout=30, index=INDEX):
        self.model = GPTModel()
        self.tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')
        self.es = Elasticsearch(host=host, port=port, timeout=timeout, index=index)
        self.index = index

    def _query(self, key, value, size=1000, exclude=None, cluster_output=True):
        '''Main search loop. clusters = {cluster1: [value1, value2…], cluster2: [..], etc.}'''
        es_query = self._create_query(key, value, exclude)
        res = self.es.search(index=self.index, body=es_query, size=size)
        titles = [x['_source']['title'] for x in res['hits']['hits']]
        vecs = [self._str_to_vec(x) for x in tqdm(titles)] # currently slow since not in batches
        outp = dict(zip(titles, vecs))
        if not cluster_output:
            return outp
        else:
            clusters, extra_info = self._titles_to_cluster(outp)
            return outp, clusters, extra_info

    def _create_query(self, key, value, exclude=None):
        '''key: e.g. subreddit or title, # value: search term or keyword
        TODO: exclude list query not implemented yet'''
        if not exclude:
            query = {"query" : {"match": {key: value}}}
        else:
            pass
        return query

    def _str_to_vec(self, s):
        '''Method to get model representation from sentence'''
        x = torch.LongTensor(self.tokenizer.encode(s)).view(1,-1)
        vec = self.model(x).squeeze()
        return vec[0]

    def _titles_to_cluster(self, outp):
        df = {k:v.tolist() for k,v in outp.items()}
        df = pd.DataFrame(df).T
        tsne = TSNE(n_components=2, perplexity=30) # dim reduction algorithm
        df_2d = pd.DataFrame(tsne.fit_transform(df), columns=['x1', 'x2'], index=df.index)
        df_2d = df_2d.apply(lambda x:(x.astype(float) - min(x))/(max(x)-min(x)), axis = 0) # scaling to aid clustering
        dbs = DBSCAN(n_jobs=-1, eps=0.1) # clustering algorithm
        cluster_assignment = dbs.fit_predict(df_2d)
        df_2d['cluster'] = cluster_assignment
        df_clusters = df_2d.reset_index().groupby('cluster')['index'].apply(lambda x: list(x))
        return dict(df_clusters), df_2d