from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy() 

from .bill import Bill #bill 클래스
from .vote import Vote #vote 클래스
from .view import View #view 클래스스