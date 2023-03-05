from abc import ABC, abstractmethod


class Device(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
