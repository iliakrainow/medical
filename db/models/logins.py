def config(db):
    class logins(db.Model):

        def __init__(self, login, hashed_password):
            self.login = login
            self.hashed_password = hashed_password
        login = db.Column(db.String(100), primary_key=True)
        hashed_password = db.Column(db.String(500))
    return logins
