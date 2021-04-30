import zmq
import cv2 as cv
import numpy as np

from mycodec import decode


port = 5555
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{port}")


while True:
    message = socket.recv_string()
    frame = decode(message)
    frame = frame.astype(np.uint8)
    cv.imshow("Torres del paine", frame)
    cv.waitKey(10)
    socket.send(b"ready")
