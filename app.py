from flask import Flask
app = Flask(__name__)

from views import flash_ssd_simulation
from views import cell_simulator
from views import paper