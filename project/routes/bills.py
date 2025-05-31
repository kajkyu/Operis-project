from flask import Blueprint,jsonify,request, render_template
from models import db, Bill, Vote, View

bp=Blueprint('bills',__name__,url_prefix='/bills')

@bp.route('/') #전체 법안 목록
def list_bills():
    bills=Bill.query.all()
    return render_template('bills/list.html',bills=bills)

@bp.route('/<int:bill_id>')
def bill_detail(bill_id):
    bill=Bill.query.get_or_404(bill_id)
    votes=Vote.query.filter_by(bill_id=bill.id).all()
    views=View.query.filter_by(bill_id=bill.id).count()

    agree_count=sum(1 for v in votes if v.is_agree)
    disagree_count=len(votes)-agree_count
    total_votes=len(votes)
    agree_ratio=(agree_count / total_votes *100) if total_votes>0 else 0

    return render_template(
        'bills/detail.html',
        bill=bill,
        views=views,
        agree_count=agree_count,
        disagree_count=disagree_count,
        agree_ratio=agree_ratio,
    )

@bp.route('/<int:bill_id>/vote',methods=['POST'])
def vote(bill_id):
    bill=Bill.query.get_or_404(bill_id)
    data=request.get_json()
    is_agree=data.get('is_agree')
    if is_agree not in [True,False]:
        return jsonify({'error':'Invalid vote value'}),400
    vote=Vote(bill_id=bill.id,is_agree=is_agree)
    db.session.add(vote)
    db.session.commit()
    return jsonify({'message':'Vote recorded'})

@bp.route('/<int:bill_id>/view',methods=['POST'])
def add_view(bill_id):
    bill=bill.query.get_or_404(bill_id)
    view=View(bill_id=bill.id)
    db.session.add(view)
    db.session.commit()
    return jsonify({'message':'View counted'})