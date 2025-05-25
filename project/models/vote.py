from . import db

class Vote(db.Model):
    __tablename__='votes'

    id=db.Column(db.Integer,primary_key=True)
    bill_id=db.Column(db.Integer,db.ForeignKey('bills.id'),nullable=False)
    upvotes=db.Column(db.Integer,default=0)
    downvotes=db.Column(db.Integer,default=0)

    bill=db.relationship('Bill',backref=db.backref('votes',uselist=False))