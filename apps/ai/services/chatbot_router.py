from .chatbot_db import database_reply
from .chatbot_ai import ai_reply

from .intents import DATABASE_INTENTS


def chatbot_reply(user, message):

    text = message.lower()

    for word in DATABASE_INTENTS:

        if word in text:

            return database_reply(user, text)

    return ai_reply(text)