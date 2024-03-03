from app import app
from flask import render_template
@app.route('/cell_simulator')
def cell_simulator():
    return render_template('cell_simulator.html')