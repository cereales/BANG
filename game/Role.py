
class Role:
    def __init__(self, id, name, desc):
        self.id = id
        self.name = name
        self.desc = desc

    def get_id(self):
        return self.id

    def is_sherif(self):
        return self.name == "Sherif"

    def is_adjoint(self):
        return self.name == "Adjoint"

    def is_renegat(self):
        return self.name == "Renegat"

    def is_outlaw(self):
        return self.name == "Hors-la-loi"
