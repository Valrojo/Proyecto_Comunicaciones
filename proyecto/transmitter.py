import zmq
from camera import CameraReader
from mycodec import denoise, code

port = 5555
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(f"tcp://localhost:{port}")

cam = CameraReader()
vid_height, vid_width = cam.get_resolution()
print("Resolución del video: {0}x{1}p".format(vid_width, vid_height))
print("Cuadros por segundo: {0}".format(cam.get_fps()//2))

#Para saltar un frame
count=0

for frame in cam:
    if(count%2==0):
       frame_denoise = denoise(frame)  
       message = code(frame_denoise)
       socket.send_json(message)
       status = socket.recv()
    count+=1
    # print(status)
    
