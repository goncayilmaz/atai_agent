import json

"""
1. get imdb id from the wikidata
"""

def initialize():
    loadImagesFile()
    return getTypes()

def loadImagesFile():
    global data
    # Opening JSON file
    f = open('data/images.json')
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    return data

def getTypes():
    global types
    types = []
    for e in data:
        if e['type'] not in types:
            types.append(e['type'])
    return types

def getImage(imdb_id, image_type, context = 'movie'):
    id_key = 'movie'
    if(context == 'human'):
        id_key = 'cast'
    for e in data:
        if imdb_id in e[id_key] and image_type == e['type']:
            return e['img']
    return ''