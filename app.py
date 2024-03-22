from flask import Flask, request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
from views import flash_ssd_simulation
from views import cell_simulator
from views import paper

# from views import sitemap_xml

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# # Initialize SQLAlchemy instance
db = SQLAlchemy(app)

# # Define a model for the database table
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)

# # Create the database tables
@app.route('/create_db')
def create_db():
    db.create_all()
    return 'Database created'

@app.route('/insert_data' , methods=['POST'])
def insert_data():
    value = request.json.get('value')
    if not value:
        return jsonify({'message': 'No value provided.'}), 400
    sum_value = db.session.query(func.sum(Data.value)).scalar()
    num_rows = db.session.query(func.count(Data.id)).scalar()
    average_waf = (sum_value + value)/(num_rows + 1)
    new_data = Data(value=average_waf)
    db.session.add(new_data)
    db.session.commit()
    return jsonify({'message': 'Data inserted successfully.'})

@app.route('/get_data' , methods=['GET'])
def get_data():
    data = Data.query.all()
    data = [{'y': d.value} for d in data]
        
    return jsonify(data)

@app.before_request
def redirect_to_domain():
    if request.host.startswith('3.89.197.36') and request.host.endswith(':3000'):
        return redirect('https://ssd.qbithabib.com', code=301)

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])