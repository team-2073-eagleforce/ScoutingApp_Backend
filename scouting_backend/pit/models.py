from scouting_backend import db


class PitEntry(db.Model):
    __tablename__ = 'PitEntry'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.Integer)
    comp_code = db.Column(db.String(16))
    drive_train = db.Column(db.String(32))
    robot_type = db.Column(db.String(10)) # Defense or Offensive
    prefer_to_score = db.Column(db.Text())
    hub = db.Column(db.String(5)) # Upper or Lower
    auto = db.Column(db.String())
    climb = db.Column(db.String(12)) # No climb or lower or mid or high or transversal
    comments = db.Column(db.Text())
    submitted_by = db.Column(db.String(30))
    image_url = db.Column(db.Text())

    def __repr__(self):
        return '<{team}-{comp}>'.format(team=self.team, comp=self.comp_code)
