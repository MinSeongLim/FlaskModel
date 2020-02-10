import requests
import json
import csv
import pandas as pd
import numpy as np
import tensorflow as tf
import time

res = requests.get('http://59.20.218.206:8080/fems/api/operation/20191001/20191130')

df = pd.read_json(res.text)

df.to_csv('./op_data.csv')

for i, row in df.iterrows():
    pass_set = [315, 330, 342]
    # if i not in pass_set:
    #     continue            
    
    print(i, row['hOpCode'])
    facility_code = "%04d" % row['facilityCode']
    pressCode = row['pressCode']
    strDateTime = row['strDateTime']
    endDateTime = row['endDateTime']
    
    gas = requests.get('http://59.20.218.206:8080/fems/api/log/%s/%s/%s/%s' % (facility_code ,'0100', strDateTime, endDateTime))
    temp = requests.get('http://59.20.218.206:8080/fems/api/log/%s/%s/%s/%s' % (facility_code, '0500', strDateTime, endDateTime))
        
    gas = pd.read_json(gas.text)
    temp = pd.read_json(temp.text)
    
        
    total_data = pd.DataFrame(list(zip(gas['dateTime'].tolist(), gas['amount'], temp['accu'])), columns=['dateTime','gas','temp'])   
    total_data.head()
     
    dataset = {}

    dataset = np.array(list(zip(total_data['gas'].values.tolist(), total_data['temp'].values.tolist())))

    

    def get_heat_finish_index(data):
        for i in range(len(data)):
            if data[i] >= 1250:
                return i
        return -1


    data = dataset    
    dataset = data[get_heat_finish_index(data[:,1])+1: len(dataset)]


    def data_transform(data):
        result = []
        last_index = len(data)
        for i in range(last_index):
            result.append([i,
                        sum(data[:i,0]),
                        data[i,1],
                        last_index])
        return result


    seq_data = {}

    seq_data = data_transform(dataset)


    lookback = 10
    step = 1

    xy = []

        
    seq_len = len(seq_data)
    for i in range(0, seq_len, step):
        if i + lookback >= seq_len:
            break
        xy.append(seq_data[i:i+lookback])
            
    xy = np.array(xy)



    min_val = np.array([np.min(xy[:,:,0]), np.min(xy[:,:,1]), np.min(xy[:,:,2]), 0])
    max_val = np.array([np.max(xy[:,:,0]), np.max(xy[:,:,1]), np.max(xy[:,:,2]), 1])


    for i, data in enumerate(xy):
        xy[i] = (data - min_val) / (max_val - min_val)
        #print((data - min_val) / (max_val - min_val))
        #break



    data_x_set =  [] #학습 데이터셋
    data_y_set =  [] #학습 데이터셋

    for data in xy:
        data_x_set.append( data[:,0:3] )
        data_y_set.append( data[:,3] )

    data_x_set =  np.array(data_x_set)
    data_y_set =  np.array(data_y_set)
   

    #print(data_x_set)
    url = 'http://localhost:5000/t/1'


    response = requests.post(url, headers = {'Content-Type': 'application/json; charset=utf-8'} , data = json.dumps({'data' : data_x_set.tolist()}))
    time.sleep(5)