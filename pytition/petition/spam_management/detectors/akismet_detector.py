from .base import BaseSpamDetector
from bs4 import BeautifulSoup
from django.conf import settings
import akismet
from petition.helpers import send_mail_to_moderation_info
from django.utils.translation import gettext as _

class AkismetSpamDetector(BaseSpamDetector):
    def is_spam(self, petition, pytitionuser) -> int:
        # initialize Akismet

        config = akismet.Config(key=settings.AKISMET_KEY, url=settings.AKISMET_URL)
        akismet_client = akismet.SyncClient.validated_client(config=config)
        # get the needed content to check it the petition is spam
        soup = BeautifulSoup(petition.text, "html.parser")
        text_msg = soup.get_text(separator = " ")
        clean_text_msg = ' '.join(text_msg.split())

        content = str(petition.title) + " " + clean_text_msg
        
        # Use akismet.check to see if spam. Returns 0: not spam, 1: possible spam, 2: definite spam. If Akismet doesn't work return 0 and send mail to moderation
        try:
            is_spam = akismet_client.comment_check(petition.ipaddr,
                                    user_agent = petition.user_agent,
                                    comment_type = "blog-post",
                                    comment_author = pytitionuser.username,
                                    comment_author_email = pytitionuser.user.email,
                                    comment_content = content, 
                                    is_test = 1 if settings.DEBUG else 0) # is_test to change in production
        except Exception as e:
            is_spam = 0
            send_mail_to_moderation_info(settings.MODERATION_EMAIL, _("Akismet is down: {e}").format(e=e))
     
        return is_spam