import pydotenv

class Environment:

    __instance = None

    @staticmethod
    def __instance__():
        if Environment.__instance == None:
            Environment()

        return Environment.__instance

    def __init__(self):
        if Environment.__instance is not None:
            raise Exception('The class already have an instance')
        else:
            self.get = pydotenv.Environment()
            Environment.__instance = self
