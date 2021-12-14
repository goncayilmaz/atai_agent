# intentions
UNKNOWN = -1
GREETING = 0
GOODBYE = 1
LOCATION = 2
TIME = 3
PERSON = 4
RECOMMENDATION = 5
IMAGE = 6

# context
MOVIE_CONTEXT = 10
ACTOR_CONTEXT = 11

# predicates
MOVIE_PREDICATE = dict(film_loc = 'P915', image = 'P18', subject = 'P921', country = 'P495', time = 'P577', cast = 'P161')
HUMAN_PREDICATE = dict(birth = 'P569', occupation = 'P106', nationality = 'P27', residence = 'P551', award = 'P166', image = 'P18')

GREETINGS_LIST = ['hey', 'hi', 'hoi', 'hello']
ASK_MOVIE_INFO_GIVEN_NAME_LIST = {}
ASK_REC_GIVEN_MOVIE_NAME_LIST = {}
ASK_REC_GIVEN_ACTOR_LIST = {}
ASK_ACTOR_INFO_GIVEN_NAME_LIST = {}
GOODBYE_LIST = ['bye', 'see you', 'see ya', 'take care', 'goodbye']
LINK_LIST = ['link', 'wikidata', 'imdb', 'webpage', 'page']

# CONTEXT_LABELS = ['actor', 'movie', 'genre', 'director']
# INTENT_LABELS = ["location", "time", "person", "recommendation", "image"]

CANDIDATE_LABELS_MOVIE = ["character", "genre", "director", "screenwriter", "cast", "producer"]
CANDIDATE_LABELS_HUMAN = ["personal information", "occupation", "award", "birth", "residence", "gender", "movie"]
CANDIDATE_LABELS_IMAGE = ['behind_the_scenes', 'still_frame', 'publicity','event', 'poster', 'production_art','product','unknown','user_avatar']
CONTEXT_LABELS = ["movie", "human"]
INTENT_LABELS = ["location", "time", "person", "recommendation", "image", "greeting", "goodbye"]

DEFAULT_MESSAGE = 'I do not know how to help you. Could you rephrase the questions?'