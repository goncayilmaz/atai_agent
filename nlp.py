from transformers import pipeline
import constant

previous_token = ""
previous_entity = ""

def initializePipelines():
    global classifier, ner_pipeline
    classifier = pipeline("zero-shot-classification")
    ner_pipeline = pipeline('ner')

"""
Returns the intent of the question
"""
def getIntend(msg):
    return classifier(msg, constant.INTENT_LABELS)

def getMovieSpecificLabel(msg):
    return classifier(msg, constant.CANDIDATE_LABELS_MOVIE)

def getHumanSpecificLabel(msg):
    return classifier(msg, constant.CANDIDATE_LABELS_HUMAN)

def getImageSpecificLabel(msg):
    return classifier(msg, constant.CANDIDATE_LABELS_IMAGE)

def getTokenList(msg):
    global previous_token
    entities = ner_pipeline(msg)
    entity_labels = []
    for entity in entities:
        print(f'entity[word]: {entity}')
        if(len(entity['word']) > 2 and entity['word'][:2] == '##' and len(entity_labels) != 0):
            entity_labels[-1] = entity_labels[-1] + entity['word'][2:]
        elif(len(entity['word']) > 0 and entity['word'] != ' '):
            entity_labels.append(entity['word'])
    if len(entity_labels) == 0:
        print(f'returning previous token: {entity_labels}')
        return [previous_token]
    res = ' '.join([str(item) for item in entity_labels])
    previous_token = res
    print(f'entity labels res: {res}')
    return [res]

def getEntityWithType(msg):
    global previous_token
    entities = ner_pipeline(msg)
    entity_labels = []
    type = 'movie'
    for entity in entities:
        print(f'entity[word]: {entity}')
        if(entity['entity'] == 'I-PER'):
            type = 'human'
        if(len(entity['word']) > 2 and entity['word'][:2] == '##' and len(entity_labels) != 0):
            entity_labels[-1] = entity_labels[-1] + entity['word'][2:]
        elif(len(entity['word']) > 0 and entity['word'] != ' '):
            entity_labels.append(entity['word'])
    if len(entity_labels) == 0:
        print(f'returning previous token: {entity_labels}')
        return [previous_token]
    res = ' '.join([str(item) for item in entity_labels])
    previous_token = res
    print(f'entity labels res: {res}')
    return [res, type]

def main():
    print('hey')

if __name__ == "__main__":
    main()
    

    