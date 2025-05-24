from flask import Blueprint, render_template, request
from models.bill import Bill

search_bp = Blueprint('search', __name__, url_prefix='')

@search_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query:
        results = Bill.query.filter(
            (Bill.title.contains(query)) | (Bill.content.contains(query))
        ).all()
    else:
        results = []
    return render_template('search.html', query=query, results=results)
