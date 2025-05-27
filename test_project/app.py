from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy

# 현재 파일의 디렉토리 경로를 가져옵니다
# os.path.dirname(__file__)는 현재 실행 중인 파일(app.py)의 디렉토리 경로를 반환합니다
# os.path.join()을 사용하여 현재 디렉토리와 'templates' 폴더를 결합합니다
# os.path.abspath()를 사용하여 절대 경로로 변환합니다
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))

# Flask 애플리케이션을 생성할 때 template_folder 파라미터를 명시적으로 지정합니다
# 이는 Flask가 템플릿 파일을 찾을 위치를 정확히 알 수 있게 해줍니다
# __name__은 현재 모듈의 이름을 나타내며, Flask가 애플리케이션의 루트 디렉토리를 찾는데 사용됩니다
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your-secret-key'  # 세션을 위한 시크릿 키

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 댓글 모델 정의
class Comment(db.Model):
    """
    댓글을 저장하는 데이터베이스 모델
    
    Attributes:
        id (int): 댓글의 고유 식별자
        bill_id (int): 댓글이 달린 법안의 ID
        content (str): 댓글 내용
        author (str): 댓글 작성자
        created_at (datetime): 댓글 작성 시간
    """
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """댓글 객체를 딕셔너리로 변환하는 메서드"""
        return {
            'id': self.id,
            'bill_id': self.bill_id,
            'content': self.content,
            'author': self.author,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()

# 샘플 데이터
bills = [
    {
        'id': 1,
        'title': '기본소득법',
        'content': '모든 국민에게 매월 기본소득을 지급하는 법안입니다.',
        'proposer': '김철수 의원',
        'date': '2024-03-01',
        'views': 1500,
        'agree': 1200,
        'disagree': 300
    },
    {
        'id': 2,
        'title': '환경보호법 개정안',
        'content': '탄소배출량을 줄이기 위한 법안입니다.',
        'proposer': '이영희 의원',
        'date': '2024-03-02',
        'views': 2000,
        'agree': 800,
        'disagree': 1200
    }
]

@app.route('/')
def index():
    # 최대 찬성, 최대 반대, 최다 조회, 최소 조회 법안 찾기
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
        # 해당 법안의 댓글들을 가져옴
        comments = Comment.query.filter_by(bill_id=bill_id).order_by(Comment.created_at.desc()).all()
        return render_template('bill_detail.html', bill=bill, comments=comments)
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

# 검색 기능을 처리하는 라우트
# GET 메소드로 /search URL에 접근할 때 실행됨
@app.route('/search', methods=['GET', 'POST'])
def search():
    global bills  # bills를 전역 변수로 선언
    # URL의 쿼리 파라미터에서 'q' 값을 가져옴
    # 'q' 파라미터가 없으면 빈 문자열('')을 기본값으로 사용
    query = request.args.get('q', '')
    
    if query:
        # 검색어가 있는 경우
        # bills 리스트에서 검색어를 포함하는 법안들을 찾음
        # 검색 조건:
        # 1. 법안 제목(title)에 검색어가 포함되어 있거나
        # 2. 법안 내용(content)에 검색어가 포함되어 있는 경우
        # 검색은 대소문자를 구분하지 않음 (lower() 메소드 사용)
        results = [bill for bill in bills if query.lower() in bill['title'].lower() or query.lower() in bill['content'].lower()]
    else:
        # 검색어가 없는 경우 빈 리스트 반환
        results = []
    
    # search.html 템플릿을 렌더링하면서 다음 변수들을 전달:
    # 1. query: 사용자가 입력한 검색어
    # 2. results: 검색 결과로 찾은 법안들의 리스트
    return render_template('search.html', query=query, results=results)

# 댓글 작성 API
@app.route('/api/comments', methods=['POST'])
def create_comment():
    """
    새로운 댓글을 생성하는 API 엔드포인트
    
    Request Body:
        - bill_id: 법안 ID
        - content: 댓글 내용
        - author: 작성자 이름
    
    Returns:
        - 성공 시: 생성된 댓글 정보와 201 상태 코드
        - 실패 시: 에러 메시지와 400 상태 코드
    """
    data = request.get_json()
    
    if not all(key in data for key in ['bill_id', 'content', 'author']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    try:
        comment = Comment(
            bill_id=data['bill_id'],
            content=data['content'],
            author=data['author']
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# 댓글 조회 API
@app.route('/api/comments/<int:bill_id>', methods=['GET'])
def get_comments(bill_id):
    """
    특정 법안의 댓글 목록을 조회하는 API 엔드포인트
    
    Args:
        bill_id: 법안 ID
    
    Returns:
        - 성공 시: 댓글 목록과 200 상태 코드
        - 실패 시: 에러 메시지와 400 상태 코드
    """
    try:
        comments = Comment.query.filter_by(bill_id=bill_id).order_by(Comment.created_at.desc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 댓글 삭제 API
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """
    특정 댓글을 삭제하는 API 엔드포인트
    
    Args:
        comment_id: 삭제할 댓글의 ID
    
    Returns:
        - 성공 시: 성공 메시지와 200 상태 코드
        - 실패 시: 에러 메시지와 400 상태 코드
    """
    try:
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': '댓글이 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 