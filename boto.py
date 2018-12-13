"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request
import json, re, random, requests

BAD_WORD_API_NAME = 'nehoraigold'
BAD_WORD_API_KEY = '8TahuZvfK4tCThrOh2L7LkvaGxUNFa8dcVIMCMuwpNwefDCU'
NO_WORDS = ("not", "no", "n't", 'incorrect', 'wrong')
YES_WORDS = ('yeah', 'yes', 'mhm', 'yep', 'correct', 'right', 'yup')
GREETING_WORDS = ("hello", "hi", "shalom", "bonjour", "alo", "what's up", "sup", "what is up", "greetings", "hey")
NAME_PREFIXES = ("i am", "i'm", "my name is", "my name's")
JOKE_WORDS = ('joke', 'funny')
SONG_WORDS = ('song', 'sing')
THANK_WORDS = ("thanks", "thank")
QUESTION_PATTERN = "[?]+"
SENTENCE_PATTERN = "([\.\!\?]+)\s*"


def handle_response(input):
    if has_curse_word(input):
        return handle_curse()
    all_sentences = re.split(SENTENCE_PATTERN, input)
    all_words = input.split(' ')
    if asks_for_something(all_words, JOKE_WORDS):
        return get_joke()
    if asks_for_something(all_words, SONG_WORDS):
        return get_song()
    if any([sentence if sentence.lower().startswith(greeting) else None for sentence in all_sentences for greeting in
            GREETING_WORDS]):
        return handle_greeting()
    elif any([word if word.lower().startswith(thank_word) else None for word in all_words for thank_word in
              THANK_WORDS]):
        return "ok", "You're very welcome."
    elif re.search(QUESTION_PATTERN, input):
        sentences = re.split(SENTENCE_PATTERN, input)
        qmark_index = sentences.index("?")
        question = sentences[qmark_index - 1]
        return handle_question(question)
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


def handle_question(question):
    word_list = question.split(' ')

    return "giggling", "I think " + question.lower() + " is a really interesting question."


def asks_for_something(words_in_message, request_triggers):
    return any(
        [word if word == trigger_word else None for word in words_in_message for trigger_word in request_triggers])


def get_joke():
    url = 'https://icanhazdadjoke.com'
    headers = {
        "Accept": "text/plain",
        "User-Agent": "ITC-Chatbot-Exercise"
    }
    req = requests.get(url, headers=headers)
    joke = req.text
    return "laughing", joke


def get_song():
    SONG_LYRICS = (
        'Who let the dogs out? Who, who, who, who, who?',
        'Mama, just killed a man. Put a gun against his head. Pulled my trigger, now he\'s dead...',
        'Never gonna give you up. Never gonna let you down. Never gonna turn around and desert you.'
    )
    return 'dancing', random.choice(SONG_LYRICS)


def has_curse_word(input):
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
    return "cursing", random.choice(CURSE_RESPONSES)


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
