from flask import Blueprint,jsonify,request, render_template
from models import db, Bill, Vote, View
import jwt
from datetime import datetime
import os

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

@bp.route('/<int:bill_id>/view',methods=['POST'])
def add_view(bill_id):
    bill=bill.query.get_or_404(bill_id)
    view=View(bill_id=bill.id)
    db.session.add(view)
    db.session.commit()
    return jsonify({'message':'View counted'})

@bp.route("/vote",methods=["POST"])
def vote():
    token=request.cookies.get("token")
    if not token:
        return jsonify({"error":"로그인이 필요합니다."}),401
    
    try:
        payload=jwt.decode(token,os.getenv("JMT_SECRET_KEY"),algorithms=["HS256"])
        user_id=payload["id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"error":"토큰이 만료되었습니다."}),401
    except jwt.InvalidTokenError:
        return jsonify({"error":"유효하지 않은 토큰입니다."}) ,401
    
    data=request.get_json()
    bill_id=data.get("bill_id")
    vote_type=data.get("vote_type")

    if vote_type not in['agree','disagree']:
        return jsonify({"error":"잘못된 투표 타입입니다."}),400
    
    existing_vote=Vote.query.filter_by(user_id=user_id,bill_id=bill_id).first()
    if existing_vote:
        return jsonify({"error":"이미 투표하셨습니다."}),400
    
    is_agree=(vote_type=='agree')
    
    new_vote=Vote(user_id=user_id,bill_id=bill_id,is_agree=is_agree)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({"message":"투표가 완료되었습니다."})