def config(db):
    class patients(db.Model):

        def __init__(self, surname, name, middle_name, docs, history, login):
            self.surname = surname
            self.name = name
            self.middle_name = middle_name
            self.docs = docs
            self.history = history
            self.hashed_password = hashed_password
            self.login = login
        surname = db.Column(db.String(100))
        name = db.Column(db.String(100))
        middle_name = db.Column(db.String(100))
        docs = db.Column(db.String(10000))
        history = db.Column(db.String(10000))
        login = db.Column(db.String(100), primary_key=True)
    return patients
