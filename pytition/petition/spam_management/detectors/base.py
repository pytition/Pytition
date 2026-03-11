from abc import ABC, abstractmethod

class BaseSpamDetector(ABC):

    @abstractmethod
    def is_spam(self, petition, pytitionuser) -> int:
        pass