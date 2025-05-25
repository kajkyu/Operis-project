from . import db

class View(db.Model):
    __tablename__='views'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    count = db.Column(db.Integer, default=0)

    bill = db.relationship('Bill', backref=db.backref('views', uselist=False))