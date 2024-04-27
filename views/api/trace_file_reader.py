# Block Status as bs (0: not full, 1: full , 2: full and eraseable)

from flask import request, jsonify, session
from app import app
import re
import math
import pandas as pd
import copy
# Device Major Number,Device Minor Number,CPU Core ID, Record ID, Timestamp (in nanoseconds), ProcessID, Trace Action, OperationType, SectorNumber + I/O Size, ProcessName
lba_block_trace_dict_global = {}
ssd_block_trace_dict_global = {}
ssd_block_trace_list_global = []
max_write_count_global = 0
max_erase_count_global = 0
ssd_structure = {
        "channel": 2,
        "chip": 1,
        "die": 2,
        "plane": 4,
        "block_container": 60,
        "block": 5,
    }
block_tracer_global = 0

def parse_trace_line(line):
    # remove extra spaces 
    return_line = {}
    line = line.strip()
    line = re.sub(' +', ' ', line)
    split_dmn = line.split(',')
    return_line['Device_Major_Number'] = split_dmn[0]
    if split_dmn[1].find('+') == -1:
        trace_info_line = split_dmn[1].strip().split(' ')
        return_line['Device_Minor_Number'] = trace_info_line[0]
        return_line['CPU_Core_ID'] = trace_info_line[1]
        return_line['Record_ID'] = trace_info_line[2]
        return_line['Timestamp_nanoseconds'] = trace_info_line[3]
        return_line['ProcessID'] = trace_info_line[4]
        return_line['Trace_Action'] = trace_info_line[5]
        return_line['OperationType'] = trace_info_line[6]
        return_line['ProcessName'] = trace_info_line[7]
    else:
        split_io_size = split_dmn[1].split('+')
        except_IO_Size_ProcessName = split_io_size[0].strip().split(' ')
        return_line['Device_Minor_Number'] = except_IO_Size_ProcessName[0]
        return_line['CPU_Core_ID'] = except_IO_Size_ProcessName[1]
        return_line['Record_ID'] = except_IO_Size_ProcessName[2]
        return_line['Timestamp_nanoseconds'] = except_IO_Size_ProcessName[3]
        return_line['ProcessID'] = except_IO_Size_ProcessName[4]
        return_line['Trace_Action'] = except_IO_Size_ProcessName[5]
        return_line['OperationType'] = except_IO_Size_ProcessName[6]
        return_line['SectorNumber'] = except_IO_Size_ProcessName[7]
        IO_Size_ProcessName = split_io_size[1].strip().split(' ')
        return_line['IO_Size'] = IO_Size_ProcessName[0]
        return_line['ProcessName'] = IO_Size_ProcessName[1]
    return return_line
        
    

def read_trace_file(file):
    traces = []
    count = 0
    # read the first lines of the file its a header 
    header = file.readline().decode('utf-8')
    for line in file:
        count += 1
        trace = parse_trace_line(line.decode('utf-8'))
        traces.append(trace)
    return traces



# Allocation Scheme Algorithms ------- S1 Allocation Scheme ----------------------- 
def allocation_scheme_algorithm(allocation_scheme, block_tracer):
    global ssd_structure
    if allocation_scheme == 's1':
        channel = math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'])) % ssd_structure['channel']
        chip = block_tracer % ssd_structure['chip']
        die = math.floor(block_tracer / ssd_structure['chip']) % ssd_structure['die']
        plane = math.floor(block_tracer / (ssd_structure['die'] * ssd_structure['chip'])) % ssd_structure['plane']
        block_container = (math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'] * ssd_structure['channel'])) % ssd_structure['block_container'])
        block = math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'] * ssd_structure['channel'] * ssd_structure['block_container'])) % ssd_structure['block']
        block_id = "block" + "_" + str(channel) + "_" + str(chip) + "_" + str(die) + "_" + str(plane) + "_" + str(block_container) + "_" + str(block)
        return block_id
    elif allocation_scheme == 's2':
        channel = block_tracer % ssd_structure['channel']
        chip = math.floor(block_tracer / ssd_structure['channel']) % ssd_structure['chip']
        die = math.floor(block_tracer / (ssd_structure['chip'] * ssd_structure['channel'])) % ssd_structure['die']
        plane = math.floor(block_tracer / (ssd_structure['die'] * ssd_structure['chip'] * ssd_structure['channel'])) % ssd_structure['plane']
        block_container = (math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'] * ssd_structure['channel'])) % ssd_structure['block_container'])
        block = math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'] * ssd_structure['channel'] * ssd_structure['block_container'])) % ssd_structure['block']
        block_id = "block" + "_" + str(channel) + "_" + str(chip) + "_" + str(die) + "_" + str(plane) + "_" + str(block_container) + "_" + str(block)
        return block_id
    else:
        return None
    
def write_block(allocation_scheme, traces):
    global ssd_block_trace_dict_global
    ssd_block_trace_dict = ssd_block_trace_dict_global
    global ssd_block_trace_list_global
    ssd_block_trace_list = ssd_block_trace_list_global
    global lba_block_trace_dict_global
    lba_block_trace_dict = lba_block_trace_dict_global
    global block_tracer_global
    block_tracer = block_tracer_global
    trace_list_tracer = 0
    def delete_lba(block_trace):
        ssd_block_trace_dict[block_trace['bid']]['dpc'] += block_trace['wpc']
        ssd_block_trace_dict[block_trace['bid']]['ds'] += block_trace['aw']
        ssd_block_trace_dict[block_trace['bid']]['lba'].remove(block_trace['lba'])
        
    def add_lba(block_id, io_size, devisable_by_4, lba):
        global max_write_count_global
        if block_id in ssd_block_trace_dict:
            ssd_block_trace_dict[block_id]['aw'] += io_size
            ssd_block_trace_dict[block_id]['wpc'] += devisable_by_4
            ssd_block_trace_dict[block_id]['wc'] += 1
            ssd_block_trace_dict[block_id]['lba'].append(lba)
            if ssd_block_trace_dict[block_id]['wc'] > max_write_count_global:
                max_write_count_global = ssd_block_trace_dict[block_id]['wc']
        else:
            ssd_block_trace_dict[block_id] = {
                'aw': io_size,
                'dpc': 0,
                'wpc': devisable_by_4,
                'wc': 1,
                'bs': 0,
                'ds': 0,
                'lba': [lba],
                'ec': 0,
                'gcs': 0
            }
            # append only block_id to ssd_block_trace_list if block_id is not in ssd_block_trace_list
            if block_id not in ssd_block_trace_list:
                ssd_block_trace_list.append(block_id)
            # ssd_block_trace_list.append(block_id)

    while trace_list_tracer < len(traces):
        block_id = allocation_scheme_algorithm(allocation_scheme, block_tracer)

        io_size = int(traces[trace_list_tracer]['io_s'])/1000
        # find how many times io_size is devisable by 4 and what is remainder 
        devisable_by_4 = io_size // 4
        remainder = io_size % 4
        if remainder > 0:
            devisable_by_4 += 1
        if block_id in ssd_block_trace_dict:
            if ssd_block_trace_dict[block_id]['wpc'] + devisable_by_4 > 256:
                if ssd_block_trace_dict[block_id]['dpc'] > 0:
                    ssd_block_trace_dict[block_id]['bs'] = 2
                else:
                    ssd_block_trace_dict[block_id]['bs'] = 1
                block_tracer += 1
                block_id = allocation_scheme_algorithm(allocation_scheme, block_tracer)
        if traces[trace_list_tracer]['lba'] in lba_block_trace_dict:
            delete_lba(lba_block_trace_dict[traces[trace_list_tracer]['lba']])
            lba_block_trace_dict[traces[trace_list_tracer]['lba']] = {
                'bid': block_id,
                'aw': io_size,
                'wpc': devisable_by_4,
                'lba': traces[trace_list_tracer]['lba']
            }
            add_lba(block_id, io_size, devisable_by_4, traces[trace_list_tracer]['lba'])
        else:
            lba_block_trace_dict[traces[trace_list_tracer]['lba']] = {
                'bid': block_id,
                'aw': io_size,
                'wpc': devisable_by_4,
                'lba': traces[trace_list_tracer]['lba']
            }
            add_lba(block_id, io_size, devisable_by_4, traces[trace_list_tracer]['lba'])
        
        trace_list_tracer += 1

    block_tracer_global = block_tracer
    lba_block_trace_dict_global = lba_block_trace_dict
    ssd_block_trace_dict_global = ssd_block_trace_dict
    ssd_block_trace_list_global = ssd_block_trace_list
    
    return {
        'ssd_block_trace_dict': ssd_block_trace_dict_global,
        'ssd_block_trace_list': ssd_block_trace_list_global,
    }
                





@app.route('/upload_trace_file' , methods=['POST'])
def trace_file_reader():
    global max_write_count_global
    global max_erase_count_global
    try:
        if 'file' not in request.files:
            data = request.json
            print(data['allocation_scheme'])
            print(data['allocation_scheme'])
            print(data['allocation_scheme'])
            print(data['allocation_scheme'])
            block_trace_info = write_block(data['allocation_scheme'], data['traceList'])
            block_trace_info['max_write_count'] = max_write_count_global
            block_trace_info['max_erase_count'] = max_erase_count_global
            copy_block_trace_info = copy.deepcopy(block_trace_info)
            for block in copy_block_trace_info['ssd_block_trace_list']:
                copy_block_trace_info['ssd_block_trace_dict'][block].pop('lba', None)
            return jsonify({'message': 'File uploaded successfully', 'traces': copy_block_trace_info}), 200
            # return jsonify({'error': 'No file part'}), 400
        
        allocation_scheme = request.form['allocation_scheme']
        
        file = request.files['file']    
        file_format = file.filename.split('.')[-1]
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file_format == 'txt':
            traces = read_trace_file(file)
            print(allocation_scheme)
            print(allocation_scheme)
            print(allocation_scheme)
            print(allocation_scheme)
            block_trace_info = write_block(allocation_scheme, traces)
            
            block_trace_info['max_write_count'] = max_write_count_global
            block_trace_info['max_erase_count'] = max_erase_count_global
            return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'traces': block_trace_info}), 200
        
        elif file_format == 'csv':
            df = pd.read_csv(file, nrows=10000)
            block_trace_info = write_block(allocation_scheme, df.to_dict(orient='records'))
            return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'traces': block_trace_info}), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    
@app.route('/garbage_collection' , methods=['POST'])
def garbage_collection():
    global ssd_block_trace_dict_global
    global ssd_block_trace_list_global
    global lba_block_trace_dict_global
    global block_tracer_global
    global max_erase_count_global
    global max_write_count_global
    ssd_block_trace_dict = ssd_block_trace_dict_global
    ssd_block_trace_list = ssd_block_trace_list_global

    trace_list = []
    for block in ssd_block_trace_list:
        if ssd_block_trace_dict[block]['bs'] == 2:
            for lba in ssd_block_trace_dict[block]['lba']:
                trace_list.append({
                    'lba': lba,
                    'io_s': (ssd_block_trace_dict[block]['aw']-ssd_block_trace_dict[block]['ds'])/len(ssd_block_trace_dict[block]['lba'])*1000,
                })
                del lba_block_trace_dict_global[lba]
            
            if 'gcs' in ssd_block_trace_dict[block]:
                ssd_block_trace_dict[block]['gcs'] += (ssd_block_trace_dict[block]['wpc'] - ssd_block_trace_dict[block]['dpc'])
                
            ssd_block_trace_dict[block]['aw'] = 0
            ssd_block_trace_dict[block]['wpc'] = 0
            ssd_block_trace_dict[block]['bs'] = 0
            ssd_block_trace_dict[block]['dpc'] = 0
            ssd_block_trace_dict[block]['ds'] = 0
            if 'ec' in ssd_block_trace_dict[block]:
                ssd_block_trace_dict[block]['ec'] += 1
                
            else:
                ssd_block_trace_dict[block]['ec'] = 1
            if ssd_block_trace_dict[block]['ec'] > max_erase_count_global:
                max_erase_count_global = ssd_block_trace_dict[block]['ec']
            ssd_block_trace_dict[block]['lba'] = []
    block_trace_info = write_block('s1', trace_list)
    block_trace_info['max_erase_count'] = max_erase_count_global
    block_trace_info['max_write_count'] = max_write_count_global
    block_tracer_global = 0
    return jsonify({'message': 'Garbage Collection Done', 'traces': block_trace_info}), 200

@app.route('/write/complete' , methods=['POST'])
def complete_write():
    global ssd_block_trace_dict_global
    global ssd_block_trace_list_global
    global lba_block_trace_dict_global
    global block_tracer_global
    global max_write_count_global
    global max_erase_count_global
    max_write_count_global = 0
    max_erase_count_global = 0
    ssd_block_trace_dict_global = {}
    ssd_block_trace_list_global = []
    lba_block_trace_dict_global = {}
    block_tracer_global = 0
    return jsonify({'message': 'Write Completed'}), 200