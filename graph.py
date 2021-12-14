import rdflib
import locale
_ = locale.setlocale(locale.LC_ALL, '')
import plotly.graph_objs as go
import difflib
import constant
import random

# WD = Namespace('http://www.wikidata.org/entity')
# WDT = Namespace('http://www.wikidata.org/prop/direct/')

def loadGraphs(type = 'turtle'):
    global graph
    global movie_list
    global human_list
    global genre_list
    global character_list
    global award_list
    # Parsing the graph
    print('Parsing the graph..')
    graph = rdflib.Graph()
    graph.parse('data/14_graph.nt', format=type)
    print('Parsing done!')
    print('Reading from movies..')
    movie_list = readFromFile("data/movie_list.txt")
    print('Reading movies done!')
    print('Reading from humans..')
    human_list = readFromFile("data/human_list.txt")
    print('Reading from humans done!')
    print('Reading genres..')
    genre_list = readFromFile('data/genre_list.txt')
    print('Reading genres done!')
    print('Reading characters..')
    character_list = readFromFile('data/character_list.txt',)
    print('Reading characters done!')
    print('Writing awards..')
    award_list = readFromFile('data/award_list.txt')
    print('Writing awards done!')
    return graph

def readFromFile(filename):
    l = []
    with open(filename, 'r') as filehandle:
        filecontents = filehandle.readlines()
        for line in filecontents:
            cur = []
            # remove linebreak which is the last character of the string
            current_place = line[:-1]
            partitions = current_place.partition(' ')
            cur.append(partitions[0])
            cur.append(partitions[2])
            # add item to the list
            l.append(cur)
    return l

def getImageLinkForEntityLabel(entity_lbl, context):
    print(f'************** {entity_lbl} ***************')
    entity = getClosestMatch(entity_lbl, context)
    print(f'closest entity name: {entity}')
    if(len(entity) == 0):
        return []
    id = getId(entity[0])
    print('******s*****************************************')
    res = queryImage(id)
    if(len(res) != 0):
        return res[-1]
    return []

def getAnswerFor(entity_lbl, answerContext, intentLabel, type = 'movie'):
    print(f'************** {entity_lbl} ***************')
    entity = getClosestMatch(entity_lbl, type)
    print(f'closest entity: {entity}')
    if(len(entity) == 0):
        return []
    id = getId(entity[0])
    res_list = queryAnswer(id, context=type, answerContext=answerContext, intentLabel=intentLabel)
    return res_list

def writeFile(filename, list):
    textfile = open(filename, "w")
    for element in list:
        textfile.write(element[0] + " " + element[1] + "\n")
    textfile.close()

def getMoviesForActor(actor):
    res_list = [ str(s) for s, in graph.query('''
    PREFIX ddis: <http://ddis.ch/atai/> 
    PREFIX wd: <http://www.wikidata.org/entity/> 
    PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
    PREFIX schema: <http://schema.org/> 
    
    SELECT ?lbl WHERE {
        ?actor rdfs:label "%s"@en .
        ?movie wdt:P161 ?actor .
        ?movie rdfs:label ?lbl .
    }
    ''' % actor)]
    if(res_list == []):
        print(f'Could not find any movies for {actor}')
    print(f"Movies for {actor}: {res_list}")
    random.shuffle(res_list)
    return res_list

def queryImage(id):
    sparql_query = """
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        SELECT ?item
        WHERE {
          wd:%s wdt:P18 ?item .
        }
        """ % (id)
    results = graph.query(sparql_query)
    if(len(results) == 0):
        return results
    return [str(result.item) for result in results]

def queryAnswer(id, context = 'movie', answerContext = '', intentLabel = ''):
    p = ''
    # CANDIDATE_LABELS_MOVIE = ["character", "genre", "director", "screenwriter", "cast", "producer"]
    if(context == 'movie'):
        if(intentLabel == constant.LOCATION):
            p = 'P915'
        elif(intentLabel == constant.TIME):
            p = 'P577'
        else:
            if(answerContext == 'genre'):
                p = 'P136'
            elif(answerContext == 'director'):
                p = 'P57'
            elif(answerContext == 'screenwriter'):
                p = 'P58'
            elif(answerContext == 'cast'):
                p = 'P161'
            elif(answerContext == 'producer'):
                p = 'P162'
            elif(answerContext == 'character'):
                p = 'P674'
    elif(context == 'human'):
        if(answerContext == 'occupation'):
            p = 'P106'
        elif(answerContext == 'personal information'):
            sparql_query = """
                PREFIX wd: <http://www.wikidata.org/entity/> 
                PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
                PREFIX schema: <http://schema.org/>
                SELECT ?element
                WHERE {
                    wd:%s schema:description ?element .
                }
                """ % (id)
            results = graph.query(sparql_query)
            res_list = [str(result.element) for result in results]
            return res_list
        elif(answerContext == 'movie'):
            label = getLabelFromId(id)
            return getMoviesForActor(label)
        elif(answerContext == 'award'):
            p = 'P166'
        elif(answerContext == 'birth'):
            if(intentLabel == constant.LOCATION):
                p = 'P19'
            else:
                p = 'P569'
        elif(answerContext == 'residence'):
            p = 'P551'
        elif(answerContext == 'gender'):
            p = 'P21'
    if(p == ''):
        return []
    print(f'predicate for {context}: {p}')
    sparql_query = """
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        SELECT ?item
        WHERE {
          wd:%s wdt:%s ?element .
          ?element rdfs:label ?item
        }
        """ % (id, p)
    results = graph.query(sparql_query)
    res_list = [str(result.item) for result in results]
    return res_list

def getAnswerText(results):
    resTxt = ""
    if(results == None or len(results) == 0):
        return "Could not find the answer!"
    elif(len(results) == 1):
        return results[-1]
    elif(len(results) > 5):
        resTxt += "Some samples are "
        results = results[:5]
    for i, res in enumerate(results):
        if(i < len(results) - 2):
            resTxt += res + ", "
        elif(i < len(results) - 1):
            resTxt += res + " and " + results[-1]
    return resTxt

def getImdbIdFromEntityLabel(entity_lbl, context = 'movie'):
    print(f'************** {entity_lbl} ***************')
    entity = getClosestMatch(entity_lbl, context)
    if(len(entity) == 0):
        return []
    print(f'closest entity: {entity}')
    id = getId(entity[0])
    print(f'id: {id}')
    res_list = [ str(s.imdb_id) for s in graph.query('''
    PREFIX wd: <http://www.wikidata.org/entity/> 
    PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
    
    SELECT ?imdb_id WHERE {
        wd:%s wdt:P345 ?imdb_id .

    }
    ''' % id)]
    return res_list


def getIdForItem(s): 
    return s[s.rindex('Q'):]

def getIdsForList(res_list):
    ids = [getIdForItem(e) for e in res_list]
    return  ids

def getId(s): 
    return s[s.rindex('/')+1:]

def getClosestMatch(entity, context):
    list = []
    if(context == "movie"):
        list = movie_list
    elif(context == "human"):
        list = human_list
    labels = [i[1] for i in list]
    close_matches = difflib.get_close_matches(entity, labels)
    if(len(close_matches)!= 0):
        entity_index = labels.index(close_matches[0])
        return list[entity_index]
    return []

def getLabelFromId(id):
    l = [ str(res.lbl) for res in graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?lbl WHERE {
                wd:%s rdfs:label ?lbl .
            }
        ''' % id)]
    if(len(l) == 0):
        return ""
    return l[0]

def getAllMovies():
    return [ [str(s), str(lbl)] for s, lbl in graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?movie ?lbl WHERE {
                ?movie wdt:P31 wd:Q11424 .
                ?movie rdfs:label ?lbl .
            }
        ''')]

def getAllGenres():
    return [ [str(s), str(lbl)] for s, lbl in graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?movie ?lbl WHERE {
                ?movie wdt:P31 wd:Q483394 .
                ?movie rdfs:label ?lbl .
            }
        ''')]

def getAllCharacters():
    return [ [str(s), str(lbl)] for s, lbl in graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?movie ?lbl WHERE {
                ?movie wdt:P31 wd:Q95074 .
                ?movie rdfs:label ?lbl .
            }
        ''')]

def getAllAwards():
    return [ [str(s), str(lbl)] for s, lbl in graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?movie ?lbl WHERE {
                ?movie wdt:P31 wd:Q618779 .
                ?movie rdfs:label ?lbl .
            }
        ''')]

def getAllHumans():
    return [ [str(s), str(lbl)] for s, lbl in graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?human ?lbl WHERE {
                ?human wdt:P31 wd:Q5 .
                ?human rdfs:label ?lbl .
            }
        ''')]
    
def main():
    loadGraphs()
    # print(queryAnswer('Inception', answerContext='genre'))

if __name__ == "__main__":
    main()


    
