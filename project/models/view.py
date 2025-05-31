from . import db

class View(db.Model):
    __tablename__='views'

    id = db.Column(db.Integer, primary_key=True) #법안을 구분할 번호
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False) #검색할 법안
    
    def __repr__(self):
        return f"<View for Bill {self.bill_id}>"