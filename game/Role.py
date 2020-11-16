
class Role:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

    def is_sherif(self):
        return self.name == "Sherif"
