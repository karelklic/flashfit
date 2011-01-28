
class Parameter:
    """
    Reaction rate output constant
    """
    def __init__(self):
        self.value = 0
        self.sigma = 0
        self.fixed = False;
        self.a0minusAinf = 0

    def __str__(self):
        result = "value:%e" % self.value
        result += " sigma:%e" % self.sigma
        result += " fixed:" + str(self.fixed)
        result += " a0minusAinf:%e" % self.a0minusAinf
        return result
