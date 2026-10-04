from .base import BaseSpamDetector
from profanity_check import predict, predict_prob
from bs4 import BeautifulSoup
from django.conf import settings

class ProfanitySpamDetector(BaseSpamDetector):
    def is_spam(self, petition, pytitionuser) -> int:

        # get the needed content to check it the petition is spam
        soup = BeautifulSoup(petition.text, "html.parser")
        text_msg = soup.get_text(separator = " ")
        clean_text_msg = ' '.join(text_msg.split())

        content = str(petition.title) + " " + clean_text_msg

        # launch the predict_prob function from the alt_profanity_check library
        # it returns an array with a probability
        # we get that probability and return 0 1 or 2 depending on its value
        is_spam = predict_prob([content])
        is_spam = float(is_spam)

        if is_spam < 0.5:
            return 0
        elif is_spam < 0.8:
            return 1
        else:
            return 2