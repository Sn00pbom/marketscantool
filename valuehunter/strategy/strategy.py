from abc import ABC, abstractstaticmethod, abstractclassmethod

class Strategy(ABC):
    
    @abstractstaticmethod
    def predict(*args) -> tuple:
        return (None, None)

    @abstractclassmethod
    def get_name(cls):
        return cls.__name__
