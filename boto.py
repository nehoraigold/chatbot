"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request
import json
import re
import random
import requests

BAD_WORD_API_NAME = 'nehoraigold'
BAD_WORD_API_KEY = '8TahuZvfK4tCThrOh2L7LkvaGxUNFa8dcVIMCMuwpNwefDCU'
WEATHER_API_KEY = '77bcbb75887d4405983155951181312'
NO_WORDS = ("not", "no", 'nope', 'whatever', 'nah')
YES_WORDS = ('yeah', 'yes', 'yep', 'correct', 'right', 'yup', 'okay', 'ok', 'o.k.', "fine", 'sure')
GREETING_WORDS = ("hello", "hi", "shalom", "bonjour", "alo", "what's up", "sup", "what is up", "greetings", "hey")
NAME_PREFIXES = ('my name', 'my name\'s')
INTERROGATIVE_WORDS = ('who', 'what', 'when', 'where', 'why', 'how')
YES_NO_QUESTION_STARTERS = ('can', 'is', 'will', 'should', 'could', 'did', 'are you')
JOKE_WORDS = ('joke', 'funny', 'jokes', 'laugh')
SONG_WORDS = ('song', 'sing', 'music', 'lyrics', 'singer')
WEATHER_WORDS = ('weather', 'sunny', 'rainy', 'cloudy')
THANK_WORDS = ("thanks", "thank")
NAMES = ("aviram", "lotem", "yoav", "ariel", "yiftach", "ilana", "omer", "gilad", "ori", "ruthy")
QUESTION_PATTERN = "[?]+"
SENTENCE_PATTERN = "([\.\!\?]+)\s*"


def handle_response(input):
    if has_curse_word(input):
        return handle_curse()
    all_sentences = re.split(SENTENCE_PATTERN, input)
    all_words = input.split(' ')
    if asks_for_something(all_words, JOKE_WORDS):
        return get_joke()
    elif asks_for_something(all_words, SONG_WORDS):
        return get_song()
    elif asks_for_something(all_words, WEATHER_WORDS):
        return get_weather()
    elif any(parse_sentences(all_sentences, GREETING_WORDS)):
        return handle_greeting()
    elif any(parse_sentences(all_sentences, THANK_WORDS)):
        return "waiting", "You're very welcome."
    elif 'my name' in input.lower():
        return respond_to_name(all_words[-1])
    elif ' ' not in input and input.replace('?', '') not in INTERROGATIVE_WORDS:
        word_without_punctuation = ''.join([char if char.isalpha() else '' for char in input])
        return handle_one_word(word_without_punctuation)
    elif re.search(QUESTION_PATTERN, input):
        sentences = re.split(SENTENCE_PATTERN, input)
        qmark_index = sentences.index("?")
        question = sentences[qmark_index - 1]
        return handle_question(question)
    elif input.lower().startswith('i ') or input.lower().startswith("i'm"):
        return handle_i_sentence(input)
    elif input.lower().startswith('you ') or input.lower().startswith("you're"):
        return handle_you_sentence(input)
    elif input.lower()[-1] == "!":
        return "afraid", "No need to shout. I can hear you just fine."
    else:
        return "confused", "I'm not sure I understood you."


def handle_greeting():
    GREETING_RESPONSES = (
        "Hello there!",
        "Hi! How are you doing today?",
        "Greetings, human.",
        "Good day to you.",
        "Hey there. How's it going?"
    )
    return "excited", random.choice(GREETING_RESPONSES)


def handle_you_sentence(sentence):
    words = sentence.split(' ')
    if words[1] == "are" or words[0] == "you're":
        return "takeoff", "Nobody's ever said that about me before!"
    else:
        response = sentence.lower()
        response = response.replace("you ", "I ").replace("are", "am") + "? If you say so."
        return "afraid", response


def handle_i_sentence(sentence):
    words = sentence.split(' ')
    if words[1] == "am" or words[0].lower() == "i'm":
        return "giggling", "You certainly are."
    else:
        response = sentence.lower()
        response = response.replace('i ', 'You ').replace('you', 'me')
        response = response + "? Well, all right."
        return 'giggling', response


def handle_one_word(word):
    if word.lower() in NAMES:
        word = word[0].upper() + word[1:].lower()
        return respond_to_name(word)
    elif word.lower() in YES_WORDS:
        return get_affirmative()
    elif word.lower() in NO_WORDS:
        return get_negative()
    else:
        return "confused", "I'm not sure what you meant by {}.".format(word.lower())


def get_affirmative():
    affirmative_responses = (
        'Indeed.',
        'Of course.',
        'Affirmative.',
        'Yes, naturally.',
    )
    return "ok", random.choice(affirmative_responses)


def get_negative():
    negative_responses = (
        'No.',
        'Certainly not.',
        'Goodness, never.',
        'I don\'t believe so.',
        'Negative.'
    )
    return 'no', random.choice(negative_responses)


def handle_question(question):
    interrogative_words = \
        list(filter(lambda x: x is not None, parse_sentences(question.split(' '), INTERROGATIVE_WORDS)))
    if any(interrogative_words):
        if 'name' in question:
            if 'your' in question:
                return "heartbroke", "My name is Boto. You've forgotten already?"
            else:
                return "confused", "I can't remember. Sorry."
        question_word = interrogative_words[0][0].upper() + interrogative_words[0][1:]
        MONEY_PHRASE = (
            "That's the million-dollar question, isn't it.",
            "If I had a nickel for every time someone asked me that... I'd have... well, more than a nickel.",
            "You ask tough questions. I guess that's why they pay you the big bucks.",
            "It doesn't matter {} as long as there's a little cash in it for you. Am I right?".format(
                question_word.lower())
        )
        return_string = "{0}? {1}".format(question_word, random.choice(MONEY_PHRASE))
        return "money", return_string
    else:
        if question.lower().startswith(YES_NO_QUESTION_STARTERS):
            reply = random.choice(("y", "n"))
            return get_affirmative() if reply == 'y' else get_negative()
        return "giggling", "I think that's a really interesting question. If only I knew the answer."


def asks_for_something(words_in_message, request_triggers):
    return any(
        [word if word == trigger_word else None for word in words_in_message for trigger_word in request_triggers])


def parse_sentences(all_sentences, what_to_parse_for):
    list_of_words = [sentence if sentence.lower().startswith(trigger_word) else None for sentence in all_sentences for
                     trigger_word in what_to_parse_for]
    return list_of_words


def respond_to_name(name):
    return "inlove", "{}? What a beautiful name!".format(name)


def get_joke():
    url = 'https://api.yomomma.info/'
    req = requests.get(url)
    joke = json.loads(req.text)['joke'] + "."
    return "laughing", joke


def get_song():
    SONG_LYRICS = (
        'Who let the dogs out? Who, who, who, who, who?',
        'Mama, just killed a man. Put a gun against his head. Pulled my trigger, now he\'s dead...',
        'Never gonna give you up. Never gonna let you down. Never gonna turn around and desert you.'
    )
    lyric = random.choice(SONG_LYRICS)
    if "dog" in lyric:
        return 'dog', lyric
    else:
        return 'dancing', lyric


def get_weather():
    url = 'http://api.apixu.com/v1/current.json'
    params = {
        'key': WEATHER_API_KEY,
        'q': 'Tel Aviv'
    }
    req = requests.get(url, params)
    weather_object = json.loads(req.text)
    city = weather_object['location']['name']
    country = weather_object['location']['country']
    temp = weather_object['current']['temp_c']
    weather_desc = weather_object['current']['condition']['text'].lower()
    weather_string = "The weather in {0}, {1} is currently {2} degrees Celsius and {3}.".format(city, country,
                                                                                                str(temp), weather_desc)
    return 'bored', weather_string


def has_curse_word(input):
    # Curse word API has a limit of 50 per day for free version
    url = 'https://neutrinoapi.com/bad-word-filter'
    params = {
        'user-id': BAD_WORD_API_NAME,
        'api-key': BAD_WORD_API_KEY,
        'content': input
    }
    req = requests.post(url, params, json.dumps(params))
    response = json.loads(req.text)
    is_bad = response["is-bad"]
    return is_bad


def handle_curse():
    CURSE_RESPONSES = (
        "There's no need for language like that.",
        "Well, that was uncalled for.",
        "That's just plain inappropriate.",
        "Do you kiss your mother with that mouth? Honestly.",
        "Maybe let's lighten up on the cursing, yeah?",
        "Just so you know, I don't love the swearing."
    )
    return "crying", random.choice(CURSE_RESPONSES)


@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    animation, response = handle_response(user_message)
    return json.dumps({"animation": animation, "msg": response})


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    run(host='localhost', port=7000)


if __name__ == '__main__':
    main()
