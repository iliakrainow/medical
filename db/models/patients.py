def config(db):
    class patients(db.Model):

        def __init__(self, surname, name, middle_name, docs, history, login, cab, status, sex, dr, medications, products):
            self.surname = surname
            self.name = name
            self.middle_name = middle_name
            self.docs = docs
            self.history = history
            self.hashed_password = hashed_password
            self.login = login
            self.cab = cab
            self.status = status
            self.sex = sex
            self.dr = dr
            self.medications = medications
            self.products = products
        surname = db.Column(db.String(100))
        name = db.Column(db.String(100))
        middle_name = db.Column(db.String(100))
        docs = db.Column(db.String(10000))
        history = db.Column(db.String(10000))
        login = db.Column(db.String(100), primary_key=True)
        cab = db.Column(db.Integer)
        status = db.Column(db.String(100))
        sex = db.Column(db.String(10))
        dr = db.Column(db.String(10))
        medications = db.Column(db.String(1000))
        products = db.Column(db.String(1000))
    return patients
