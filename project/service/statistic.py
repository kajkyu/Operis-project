from models import db
from models.vote import Vote
from models.view import View

def increment_view(bill_id):
    view=view.query.filter_by(bill_id=bill_id).first()
    if not view:
        view=View(bill_id=bill_id,count=1)
        db.session.commit()
    else:
        view.count+=1
        db.session.commit()

def vote_bill(bill_id,up=True):
    vote=Vote.query.filter_by(bill_id=bill_id).first()
    if not vote:
        vote=Vote(bill_id=bill_id)
        db.session.commit()
    if up:
        vote.agree+=1
        db.session.commit()
    else:
        vote.disagree+=1
        db.sessiont.commit()