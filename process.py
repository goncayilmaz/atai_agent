import time
import constant
import random
from graph import loadGraphs, getImageLinkForEntityLabel, getAnswerFor, getAnswerText
import nlp
import recommend
import graph
import image
import os

def initialize():
    nlp.initializePipelines()
    g = loadGraphs()
    recommend.initialize(g)
    image.initialize()

class Chatbot():
    def __init__(self, room_id):
        self.previous_token = []
        self.room_id = room_id

    def getHelp(self):
        info = """
        You can ask me variety of questions such as: \n
        1) About movies: characters, genre, director, screenwriter, cast members, producer \n
        2) About people: movies, personal information, occupation, awards, birth, residence, gender \n
        3) Webpages about movies and people: wikidata pages, imdb pages \n
        4) Images: behind the scenes, events, publicity, poster, etc. \n
        5) Recommendation based on a movie, or an actor. \n
        Do not forget to evaluate my performance in the end :)
        """
        return info
    
    def getResponse(self, message):
        if(any(word in message for word in ['HELP'])):
            return self.getHelp()
        intention = self.getIntention(message)
        answer = self.getAnswer(message, intention)
        # "Got your message \"{}\" at {}.".format(message, time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime()))
        return answer

    def getIntentionCode(self, intentionStr):
        print(f'intention str: {intentionStr}')
        if(intentionStr == 'location'):
            return constant.LOCATION
        elif(intentionStr == 'time'):
            return constant.TIME
        elif(intentionStr == 'person'):
            return constant.PERSON
        elif(intentionStr == 'recommendation'):
            return constant.RECOMMENDATION
        elif(intentionStr == 'image'):
            return constant.IMAGE
        elif(intentionStr == 'greeting'):
            return constant.GREETING
        elif(intentionStr == 'goodbye'):
            return constant.GOODBYE
        return constant.UNKNOWN

    def getIntention(self, message):
        # if any(word in message for word in constant.GREETINGS_LIST):
        #    return constant.GREETING
        # elif any(word in message for word in constant.GOODBYE_LIST):
        #     return constant.GOODBYE
        # else:
        intentionStr = nlp.getIntend(message)['labels'][0]
        return self.getIntentionCode(intentionStr)

    # to answer questions
    def processContext(self, message, entity, context, intent):
        if(context == "movie"):
            label = nlp.getMovieSpecificLabel(message)['labels'][0] 
        elif(context == "human"):
            label = nlp.getHumanSpecificLabel(message)['labels'][0] 
        else:
            return constant.DEFAULT_MESSAGE
        print('************************ process context ***************************')
        print(f'label of the question: {label}')
        print(f'intent: (location, time, person etc.) {intent}')
        results = getAnswerFor(entity, label, intent, type = context)
        return getAnswerText(results)

    def processRecommendationRequest(self, entity, type = 'movie'):
        if(type == 'human'):
            entity_list = graph.getMoviesForActor(entity)
            if(len(entity_list) > 5):
                entity_list = entity_list[:5]
            return recommend.getRecommendationText(entity_list)
        prev_entity = entity
        entity = graph.getClosestMatch(entity, type)
        if(len(entity) == 0):
            print(f'closest entity name was NOT FOUND')
            return f'Could not find good recommendations for {prev_entity}. Please rephrase the question!'
        print(f'closest entity name: {entity[0]}')
        id = graph.getId(entity[0])    
        similar_list = recommend.findSimilarEntities(id)
        return recommend.getRecommendationText(similar_list)

    def processImageRequest(self, msg, entity, type):
        ids = graph.getImdbIdFromEntityLabel(entity, type)
        image_type = nlp.getImageSpecificLabel(msg)['labels'][0] 
        if(len(ids) == 0):
            return f'Sorry, I could not find the IMDb id for {entity}.'
        img = image.getImage(ids[0], image_type, type)
        if(img  == ''):
            return f'Sorry, I could not find an image for {entity}.'
        return f'image:{os.path.splitext(img)[0]}' 
    
    def processLinkRequest(self, msg, entity, type):
        if(any(word in msg for word in ['wikidata', 'wiki'])):
            prev_entity = entity
            entity = graph.getClosestMatch(entity, type)
            if(len(entity) == 0):
                print(f'closest entity name was NOT FOUND')
                return f'Could not find good recommendations for {prev_entity}. Please rephrase the question!'
            print(f'closest entity name: {entity[0]}')
            id = graph.getId(entity[0]) 
            return "wd:%s" % id
        else:
            imdb_ids = graph.getImdbIdFromEntityLabel(entity, type)
        if(imdb_ids == None or len(imdb_ids) == 0):
            return f'Sorry, I could not find the IMDb id for the associated entity.'
        return "imdb:" + str(imdb_ids[0])

    def getAnswer(self, message, intention):
        if(intention == constant.GREETING):
            rand_index = random.randint(0, len(constant.GREETINGS_LIST) - 1)
            return constant.GREETINGS_LIST[rand_index].capitalize() + '!'
        elif(intention == constant.GOODBYE):
            rand_index = random.randint(0, len(constant.GOODBYE_LIST) - 1)
            return constant.GOODBYE_LIST[rand_index].capitalize() + '!'
        elif(any(word in message for word in constant.LINK_LIST)):
            entity_type = nlp.getEntityWithType(message)
            if(len(entity_type) < 2):
                if(len(self.previous_token) < 2):
                    return constant.DEFAULT_MESSAGE
                else:
                    entity_type = self.previous_token
            else:
                self.previous_token = entity_type
            # print(f'getAnswer -- context: {context}')
            print(f'getAnswer -- entity and type: {entity_type}')
            return self.processLinkRequest(message, entity_type[0], entity_type[1])
        elif(intention == constant.RECOMMENDATION):
            entity_type = nlp.getEntityWithType(message)
            if(len(entity_type) < 2):
                if(len(self.previous_token) < 2):
                    return f'Sorry, I do not know what to recommend you. Could you specify what kind of movies you would want?'
                else:
                    entity_type = self.previous_token
            else:
                self.previous_token = entity_type
            return self.processRecommendationRequest(entity_type[0], entity_type[1])
        else:
            # context is either human or movie
            # context = getContext(message)
            # entities are extracted with NER
            entity_type = nlp.getEntityWithType(message)
            if(len(entity_type) < 2):
                if(len(self.previous_token) < 2):
                    return constant.DEFAULT_MESSAGE
                else:
                    entity_type = self.previous_token
            else:
                self.previous_token = entity_type
            # print(f'getAnswer -- context: {context}')
            print(f'getAnswer -- entity and type: {entity_type}')
            # if it is image 
            if(intention == constant.IMAGE):
                return self.processImageRequest(message, entity_type[0], entity_type[1])
            # else if it is a question
            elif(intention != constant.UNKNOWN):
                return self.processContext(message, entity_type[0], entity_type[1], intention)
                # return f'Your intention: {intention}, the context: {context}'
        return constant.DEFAULT_MESSAGE
    
    def getWaitingMessage(self):
        msgs = ['I have a really big brain. Give me few seconds while I try to find the answer!', 'Processing...', 'Okay, give me few seconds.', 'Okay, looking into it!']
        random.shuffle(msgs)
        return msgs[-1]

def main():
    initialize()
    print(getResponse('Who is the director of Batman?'))
    print(getResponse('What is the occupation of Christopher Nolan?'))
    print(getResponse('Can you recommend me a movie?'))

if __name__ == "__main__":
    main()