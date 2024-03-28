from flask import request, jsonify
from app import app
import re
import math
# Device Major Number,Device Minor Number,CPU Core ID, Record ID, Timestamp (in nanoseconds), ProcessID, Trace Action, OperationType, SectorNumber + I/O Size, ProcessName

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
    print(header)
    for line in file:
        count += 1
        trace = parse_trace_line(line.decode('utf-8'))
        traces.append(trace)
    return traces


def write_block(ssd_structure, allocation_scheme, traces):
    print(allocation_scheme)
    print(ssd_structure)
    # print(traces)
    written_block_list = []
    if allocation_scheme == 's1':
        for block_tracer in range(0, 1000):
            channel = math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'])) % ssd_structure['channel']
            chip = block_tracer % ssd_structure['chip']
            die = math.floor(block_tracer / ssd_structure['chip']) % ssd_structure['die']
            plane = math.floor(block_tracer / (ssd_structure['die'] * ssd_structure['chip'])) % ssd_structure['plane']
            block_container = math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'])) % ssd_structure['block_container']
            block = math.floor(block_tracer / (ssd_structure['plane'] * ssd_structure['die'] * ssd_structure['chip'] * ssd_structure['block_container'])) % ssd_structure['block']
            # print(channel, chip, die, plane, block)
            written_block_list.append(
                {
                    'block_id': "block" + "_" + str(channel) + "_" + str(chip) + "_" + str(die) + "_" + str(plane) + "_" + str(block_container) + "_" + str(block),
                    'written_size_kb': 0,
                    'free_size': 0,
                    'status': 0,
                    'test': 0
                }
            )
    print(written_block_list)
            
    return written_block_list
    




@app.route('/upload_trace_file' , methods=['POST'])
def trace_file_reader():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    allocation_scheme = request.form['allocation_scheme']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file.filename.split('.')[-1] == 'txt':
        traces = read_trace_file(file)
        ssd_structure = {
            "channel": 2,
            "chip": 1,
            "die": 2,
            "plane": 4,
            "block_container": 60,
            "block": 5,
        }
        block_trace_info = write_block(ssd_structure, allocation_scheme, traces)
        
            
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'traces': block_trace_info}), 200
    elif file.filename.split('.')[-1] != 'csv':
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400