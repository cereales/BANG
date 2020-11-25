
class Character:
    def __init__(self, id, name, life):
        self.id = id
        self.name = name
        self.max_life = life

    def get_id(self):
        return self.id
