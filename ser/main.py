from flask import Flask, Response, request
from flask_socketio import SocketIO, emit, send
import cv2
import time
from itertools import count
from multiprocessing import Process
from threading import Thread
from queue import Queue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')


@socketio.on("connect")
def is_connect():
    print("connected")


@socketio.on("disconnect")
def is_disconnect():
    print("disconnected")


# def gen():
#     i = 0
#     cap = cv2.VideoCapture(i)
#     while True:
#             success, image = cap.read()
#             # to replay video infinitely
#             if not success:
#                 cap = cv2.VideoCapture(i)
#                 success, image = cap.read()
#                 image = image.encode("utf-8")
#             _, encoded = cv2.imencode(".jpg", image)
#             print("encoded")
#             yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
#                     bytearray(encoded) + b'\r\n')
que = Queue()


class Camera:
    def __init__(self, camera_on=False):
        self.path = int(0)
        self.cap = cv2.VideoCapture(self.path)
        self.camera_on = bool(camera_on)
        print(type(self.path), self.path)

    def get_frame(self):
        while True:
            success, image = self.cap.read()
            # to replay video infinitely
            if not success:
                self.cap = cv2.VideoCapture(self.path)
                success, image = self.cap.read()
                image = image.encode("utf-8")
            _, encoded = cv2.imencode(".jpg", image)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encoded) + b'\r\n')


@app.route('/video_feed')
def video_feed():
    ca = bool(request.args.get("camera_on"))
    print(ca)
    t = Thread(target=lambda q, arg1: q.put(
        Camera(ca).get_frame()), args=(que, 'world!'))
    t.start()
    t.join()

    return Response(que.get(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    # return Response(gen(),mimetype='image/svg; boundary=frame')

@socketio.on("clicapture")
def passChat(chat):
    # print(chat)
    socketio.emit("sercapture", chat, callback=messageReceived)

@socketio.on("PassChat")
def passChat(chat):
    # print(chat)
    socketio.emit("fromServer", chat, callback=messageReceived)


@socketio.on("typing")
def passChat(chat):
    Process(target=sendTyping(chat), name='chat_typing').start()


def sendTyping(chat):
    # print(chat)
    socketio.emit("isTypeing", "{} กำลังพิมพ์...".format(
        str(chat['name'])), callback=messageReceived)


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


# class Camera:
#     def __init__(self, index=0):
#         self.path = int(index)
#         self.cap = cv2.VideoCapture(self.path)
#         # print(type(self.path), self.path)
#     def thred(self):
#         Process(target=self.get_frame(), name='chat_typing').start()
#
#     def get_frame(self):
#         for i in range(120):
#             success, image = self.cap.read()
#             # to replay video infinitely
#             if not success:
#                 self.cap = cv2.VideoCapture(self.path)
#                 success, image = self.cap.read()
#                 image = image.encode("utf-8")
#             _, encoded = cv2.imencode(".jpg", image)
#             yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
#                    bytearray(encoded) + b'\r\n')
#         self.cap.release()


#
# @socketio.on("onStream")
# def onStream(index=0):
#     print("open V")
#     for video_frame in Camera(index).thred():
#         socketio.emit('broadcast', video_frame, callback=messageReceived);
#     print("sent")


def get_frame(path=0):
    cap = cv2.VideoCapture(path)
    while True:
        success, image = cap.read()
        # to replay video infinitely
        if not success:
            _cap = cv2.VideoCapture(path)
            success, image = cap.read()
            image = image.encode("utf-8")
        _, encoded = cv2.imencode(".jpg", image)
        socketio.emit('broadcast',  (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                                     bytearray(encoded) + b'\r\n'), callback=messageReceived)



if __name__ == '__main__':
    counter = count(0)
    socketio.run(app)
