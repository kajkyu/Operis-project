from flask import Flask
from flask import redirect
from models import db
from routes.bills import bp as bills_bp

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///bills.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='your-secret-key'

db.init_app(app)

app.register_blueprint(bills_bp)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)