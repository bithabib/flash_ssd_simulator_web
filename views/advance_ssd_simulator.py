from app import app
from flask import render_template, session
@app.route('/advance_ssd')
def advance_ssd_simulator():
    # ssd_block_trace_dict = {}
    # ssd_block_trace_list = []
    # lba_block_trace_dict = {}
    # block_tracer = 0
    session['ssd_block_trace_dict'] = {}
    session['ssd_block_trace_list'] = []
    session['block_tracer'] = 0
    return render_template('advance_ssd_simulator.html')