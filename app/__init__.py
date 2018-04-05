from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.DEBUG=True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)



@app.route('/', methods=['GET', 'POST'])
def index():
    print("in index")
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/test')
def test_connect():
    print("in connect")
    global thread
    #with thread_lock:
    #    if thread is None:
    #        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('my_event', namespace='/test')
def test_message(message):
    print(" in test_message: %s" % message)
    session['receive_count'] = session.get('receive_count', 0) + 1
    #session['receive_count'] = session.get('receive_count', 0) + 1
    #emit('my_response', {'data': message['data'], 'count': session['receive_count']})
    emit('my_response', {'data': message['data'], 'count': session['receive_count']})

@socketio.on('my_broadcast_event', namespace='/test')
def handle_message(message):
    print('received message: ' + message)

if __name__ == '__main__':
    socketio.run(app, debug=True)
