
class Character:
    def __init__(self, name, life):
        self.name = name
        self.life = life
        self.max_life = life

    def increase_max_life(self):
        self.max_life += 1
