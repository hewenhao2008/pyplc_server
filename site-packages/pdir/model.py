
class CustomString(str):

    def __init__(self, string):
        self.string = string
        super(CustomString, self).__init__()

    def __repr__(self):
        return self.string
