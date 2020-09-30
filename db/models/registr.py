def config(db):
    class registr(db.Model):
        def __init__(self, surname, name, middle_name, login):
            self.surname = surname
            self.name = name
            self.middle_name = middle_name
            self.login = login
        surname = db.Column(db.String(100))
        name = db.Column(db.String(100))
        middle_name = db.Column(db.String(100))
        login = db.Column(db.String(100), primary_key=True)
    return registr
