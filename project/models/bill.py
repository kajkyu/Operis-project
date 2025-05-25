from . import db

class Bill(db.Model):
    __tablename__='bills'

    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200),nullable=False)