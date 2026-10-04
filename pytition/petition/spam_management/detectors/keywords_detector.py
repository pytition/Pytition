from .base import BaseSpamDetector
from bs4 import BeautifulSoup
from django.conf import settings

class KeywordSpamDetector(BaseSpamDetector):
    def is_spam(self, petition, pytitionuser) -> int:
        # get the content needed to check for keywords in a petition
        soup = BeautifulSoup(petition.text, "html.parser")
        text_msg = soup.get_text(separator = " ")
        clean_text_msg = ' '.join(text_msg.split())
        content = str(petition.title) + " " + clean_text_msg
        content_list = content.split()
        content_list = [word.lower() for word in content_list]

        # check if a keyword is in content
        forbidden_words = any(word in content_list for word in settings.FORBIDDEN_WORDS)

        if forbidden_words:
            return 1
        else:
            return 0