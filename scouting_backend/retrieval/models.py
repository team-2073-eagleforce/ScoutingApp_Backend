from scouting_backend import db


class matchEntry(db.Model):
    __tablename__ = 'scouting'
    __table_args__ = {'extend_existing': True}
    
    team = db.Column(db.Integer, primary_key=True)
    matchNumber = db.Column(db.Integer)
    autoCrossing = db.Column(db.Integer)
    autoUpper = db.Column(db.Integer)
    autoBottom = db.Column(db.Integer)
    teleUpper = db.Column(db.Integer)
    teleBottom = db.Column(db.Integer)
    level = db.Column(db.Integer)
    driverPerf = db.Column(db.Integer)
    defensePerf = db.Column(db.Integer)
    name = db.Column(db.String(32))
    comment = db.Column(db.String(64))

    def __repr__(self):
        return '<{team}-{match}>'.format(team=self.team, match=self.matchNumber)
