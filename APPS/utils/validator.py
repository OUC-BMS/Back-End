from abc import ABCMeta, abstractmethod


class BaseValidator(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def validate(cls, raw_string):
        pass
