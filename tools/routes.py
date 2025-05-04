from flask import Blueprint, render_template, request
from metadata.openlibrary import get_book_data

import_bp = Blueprint('import', __name__, url_prefix='/import')

@import_bp.route('/')
def search():
    # show a page with multiple import options
    return render_template('import.html')