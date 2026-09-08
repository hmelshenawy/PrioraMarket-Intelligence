from abc import abstractmethod, ABC

class BaseAlgoliaClient(ABC):

    @abstractmethod
    def extract(self, ):

        pass

    @abstractmethod
    def getPrams(self, prams):

        pass
    