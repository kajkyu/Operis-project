from . import db

class Vote(db.Model):
    __tablename__='votes'

    id=db.Column(db.Integer,primary_key=True)
    bill_id=db.Column(db.Integer,db.ForeignKey('bills.id'),nullable=False) 
    is_agree=db.Column(db.Boolean,nullable=False)

    def __repr__(self):
        return f"<Vote{'찬성'if self.is_agree else '반대'} for bill {self.bill_id}>"