from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # ������ ���� ��ũ�� Ű

# ���� ������
bills = [
    {
        'id': 1,
        'title': '�⺻�ҵ��',
        'content': '��� ���ο��� �ſ� �⺻�ҵ��� �����ϴ� �����Դϴ�.',
        'proposer': '��ö�� �ǿ�',
        'date': '2024-03-01',
        'views': 1500,
        'agree': 1200,
        'disagree': 300
    },
    {
        'id': 2,
        'title': 'ȯ�溸ȣ�� ������',
        'content': 'ź�ҹ��ⷮ�� ���̱� ���� �����Դϴ�.',
        'proposer': '�̿��� �ǿ�',
        'date': '2024-03-02',
        'views': 2000,
        'agree': 800,
        'disagree': 1200
    }
]

@app.route('/')
def index():
    # �ִ� ����, �ִ� �ݴ�, �ִ� ��ȸ, �ּ� ��ȸ ���� ã��
    max_agree = max(bills, key=lambda x: x['agree'])
    max_disagree = max(bills, key=lambda x: x['disagree'])
    max_views = max(bills, key=lambda x: x['views'])
    min_views = min(bills, key=lambda x: x['views'])
    
    return render_template('index.html', 
                         max_agree=max_agree,
                         max_disagree=max_disagree,
                         max_views=max_views,
                         min_views=min_views,
                         bills=bills)

@app.route('/bill/<int:bill_id>')
def bill_detail(bill_id):
    bill = next((b for b in bills if b['id'] == bill_id), None)
    if bill:
        return render_template('bill_detail.html', bill=bill)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/vote/<int:bill_id>/<vote_type>', methods=['POST'])
def vote(bill_id, vote_type):
    bill = next((b for b in bills if b['id'] == bill_id), None)
    if bill:
        if vote_type == 'agree':
            bill['agree'] += 1
        elif vote_type == 'disagree':
            bill['disagree'] += 1
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

if __name__ == '__main__':
    app.run(debug=True) 