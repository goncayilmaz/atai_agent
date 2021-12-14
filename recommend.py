import numpy as np
import csv
import rdflib
import pandas as pd
from sklearn.metrics import pairwise_distances
import random

RDFS = rdflib.namespace.RDFS
WD = rdflib.Namespace('http://www.wikidata.org/entity/')

def initialize(graph):
    global entity_emb, relation_emb, id2ent, id2rel, lbl2ent, ent2id, ent2lbl
    entity_emb = np.load('data/entity_embeds.npy')
    relation_emb = np.load('data/relation_embeds.npy')

    # load the dictionaries
    with open('data/entity_ids.del', 'r') as ifile:
        ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')}
        id2ent = {v: k for k, v in ent2id.items()}
    with open('data/relation_ids.del', 'r') as ifile:
        rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')}
        id2rel = {v: k for k, v in rel2id.items()}

    ent2lbl = {ent: str(lbl) for ent, lbl in graph.subject_objects(RDFS.label)}
    lbl2ent = {lbl: ent for ent, lbl in ent2lbl.items()}

def findSimilarEntities(id):
    # which entities are similar to "Harry Potter and the Goblet of Fire"
    ent = ent2id[WD[id]] #Q102225
    # we compare the embedding of the query entity to all other entity embeddings
    dist = pairwise_distances(entity_emb[ent].reshape(1, -1), entity_emb).reshape(-1)
    # order by plausibility
    most_likely = dist.argsort()

    most_likely = most_likely[1:20]
    random.shuffle(most_likely)
    most_likely = most_likely[1:5]

    df = pd.DataFrame([
        (
            id2ent[idx][len(WD):], # qid
            ent2lbl[id2ent[idx]],  # label
            dist[idx],             # score
            rank+1,                # rank
        )
        for rank, idx in enumerate(most_likely)],
        columns=('Entity', 'Label', 'Score', 'Rank'))
    
    return df['Label'].values

def getRecommendationText(rec_list):
    resTxt = ""
    if(len(rec_list) == 0):
        return "Could not find any similar entities."
    elif(len(rec_list) == 1):
        return "My recommendation is %s." % rec_list[-1]
    resTxt += "My recommendations are "
    for i, rec in enumerate(rec_list):
        if(i < len(rec_list) - 2):
            resTxt += rec + ", "
        elif(i < len(rec_list) - 1):
            resTxt += rec + " and " + rec_list[-1] +  "."
    return resTxt


    