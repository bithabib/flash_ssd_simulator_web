from flask import request, jsonify
from app import app
import re
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


@app.route('/trace_file_converter' , methods=['POST'])
def file_converter():
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
  
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file.filename.split('.')[-1] == 'txt':
        traces = read_trace_file(file)
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'traces': traces}), 200
    elif file.filename.split('.')[-1] != 'csv':
        print("This is csv file")
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400