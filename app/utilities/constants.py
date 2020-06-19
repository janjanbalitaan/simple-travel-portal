class Constant:

    __instance = None

    @staticmethod
    def __instance__():
        if Constant.__instance == None:
            Constant()

        return Constant.__instance

    def __init__(self):
        if Constant.__instance is not None:
            raise Exception('The class already have an instance')
        else:
            Constant.__instance = self

