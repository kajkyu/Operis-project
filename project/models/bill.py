from . import db

class Bill(db.Model):
    __tablename__='bills'

    id=db.Column(db.Integer,primary_key=True) #법안을 구분할 번호
    bill_id=db.Column(db.String(100),unique=True,nullable=False) #국회 API의 고유 ID
    title=db.Column(db.String(200),nullable=False) #검색할 법안 제목을 저장할 변수 수
    summary=db.Column(db.Text) #법안 개요
    proposer=db.Column(db.String(20)) #법안 발의자
    proposal_date=db.Column(db.Date) #발의 날짜
    
    votes=db.relationship("Vote",backref="bill",lazy=True)
    views=db.relationship("View",backref="bill",lazy=True)

    def __repr__(self):
        return f"<Bill {self.title}>"