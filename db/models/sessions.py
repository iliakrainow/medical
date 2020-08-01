def config(db):
    class sessions(db.Model):

        def __init__(self, login, session, time, blocked):
            self.login = login
            self.session = session
            self.time = time
            self.blocked = blocked
        login = db.Column(db.String(100))
        session = db.Column(db.String(500), primary_key=True)
        time = db.Column(db.String(50))
        blocked = db.Column(db.Integer)
    return sessions
