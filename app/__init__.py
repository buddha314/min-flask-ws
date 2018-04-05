from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import random
import time

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
pony_thread = None
thread_lock = Lock()

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count}, namespace='/test')

def update_ponies():
    for i in range(5):
        socketio.sleep(1)
        x = random.random()
        print("i is %s" % x)
        socketio.emit('pony_update', {'data': x}, namespace='/test')

@app.route('/', methods=['GET', 'POST'])
def index():
    print("in index")
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/test')
def test_connect():
    print("in connect")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('my_event', namespace='/test')
def test_message(message):
    print(" in test_message: %s" % message)
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']})

@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    print('received message: %s' % message)
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']}, broadcast=True)

@socketio.on('the_ponies', namespace='/test')
def run_numbers(message):
    global pony_thread
    with thread_lock:
        if pony_thread is None:
            print("starting back_work")
            pony_thread = socketio.start_background_task(target=update_ponies)

if __name__ == '__main__':
    socketio.run(app, debug=True)
