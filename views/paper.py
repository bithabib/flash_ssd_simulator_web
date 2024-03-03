from app import app
from flask import render_template
@app.route('/paper')
def paper():
    return render_template('paper.html')