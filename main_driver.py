#!/usr/bin/python

import socket
import threading

from drivingsim_pb2 import DriveRequest
from drivingsim_pb2 import DriveResponse

HOST = 'localhost'
PORT = 8088


def HandleConnection(conn):
  print('new connection in %s' % threading.current_thread().ident)
  accel_m_s2 = -1.0
  while True:
    data = conn.recv(1024)
    req = DriveRequest.FromString(data)

    dist_m = req.ahead.position_m - req.current.position_m
    while dist_m < 0.0:
      dist_m += req.length_m
    if dist_m < 2.0:
      accel_m_s2 = -5 * 9.8
    elif dist_m > 50.0 and dist_m < 200.0 and accel_m_s2 < 5.0:
      accel_m_s2 = 9.8
    elif dist_m > 1.0 and accel_m_s2 < 0.0:
      accel_m_s2 = 2.0
    resp = DriveResponse(acceleration_m_s2=accel_m_s2)

    conn.sendall(resp.SerializeToString())
  print('connection closed in %s' % threading.current_thread().ident)


def ListenForConnections():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((HOST, PORT))
  print('listening on %s:%d' % (HOST, PORT))
  while True:
    sock.listen(4)
    conn, _ = sock.accept()
    thread = threading.Thread(target=HandleConnection, args=(conn,))
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
  ListenForConnections()
