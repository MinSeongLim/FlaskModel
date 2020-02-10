from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
from datetime import timedelta
import os, random, datetime
import tensorflow as tf
from flask_socketio import SocketIO, emit
import random
import numpy as np
import json

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods = ['GET'])
def realtime():
    return render_template('realtime.html')

@socketio.on('my_broadcast_event')
def test_broadcast_message(message):    
    emit(message['data']['chart'], {'data': message['data']}, broadcast=True , namespace='/test')

def run_tensor(data, facilty_code):
    
    model_name = ''
    c = ''

    if(facilty_code == '1'):
        model_name = '0301_P5_weekday.h5'
        c = '1'
    elif(facilty_code == '2'):
        model_name = '0301_P5_weekday_h.h5'
        c = '2'
    elif(facilty_code == '3'):
        model_name = '0301_P5_weekend.h5'
        c = '3'
    elif(facilty_code == '4'):
        model_name = '0301_P5_weekend_h.h5'
        c = '4'
    elif(facilty_code == '5'):
        model_name = '0303_P15_weekday.h5'
        c = '5'
    elif(facilty_code == '6'):
        model_name = '0303_P15_weekday_h.h5'
        c = '6' 
    elif(facilty_code == '7'):
        model_name = '0303_P15_weekend.h5'
        c = '7'
    else:
        model_name = '0303_P15_weekend_h.h5'
        c = '8'

    new_model = tf.keras.models.load_model(model_name)
    #new_model.summary()
    y_pred = new_model.predict(data)

    result1 = y_pred[0]   
    ress = result1.astype(int)
   
    test_broadcast_message(
        {'data' : 
            {
                'data':     data.tolist(),
                'result':   ress.tolist(),
                'chart': c
            }
        }
    )
    
    return "{result:" + str(ress) + "}"


@app.route('/t/<facilty_code>', methods= ['GET', 'POST'])
def test2(facilty_code):
    data = np.array(request.get_json('data')['data'])

    return run_tensor(data, facilty_code)

socketio.run(app, host='0.0.0.0', debug=True)