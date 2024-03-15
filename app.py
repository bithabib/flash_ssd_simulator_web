from flask import Flask, request, redirect
app = Flask(__name__)

from views import flash_ssd_simulation
from views import cell_simulator
from views import paper

@app.before_request
def redirect_to_domain():
    if request.host.startswith('3.89.197.36') and request.host.endswith(':3000'):
        return redirect('https://ssd.qbithabib.com', code=301)