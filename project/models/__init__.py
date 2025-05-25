from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

from .bill import Bill 
from .vote import Vote
from .view import View