#!/usr/bin/python

import SocketServer

from drivingsim_pb2 import DriveRequest
from drivingsim_pb2 import DriveResponse

HOST = 'localhost'
PORT = 8088


class DriverHandler(SocketServer.BaseRequestHandler):
  def __init__(self, *args, **kwargs):
    SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)
    self._accel_m_s2 = -1.0

  def handle(self):  # handles a connection
    print('new connection')
    while True:
      data = self.request.recv(1024)
      req = DriveRequest.FromString(data)
      print(
          'Drive: t=%.1fs car=%.1fm ahead=%.1fm'
          % (req.time_s, req.current.position_m, req.ahead.position_m))
      self.request.sendall(self.Drive(req).SerializeToString())
    print('connection closed')

  def Drive(self, request):
    dist_m = request.ahead.position_m - request.current.position_m
    while dist_m < 0.0:
      dist_m += request.length_m
    if dist_m < 2.0:
      self._accel_m_s2 = -5 * 9.8
    elif dist_m > 50.0 and dist_m < 200.0 and self._accel_m_s2 < 5.0:
      self._accel_m_s2 = 9.8
    elif dist_m > 1.0 and self._accel_m_s2 < 0.0:
      self._accel_m_s2 = 2.0
    return DriveResponse(acceleration_m_s2=self._accel_m_s2)


if __name__ == '__main__':
  SocketServer.TCPServer.allow_reuse_address = True
  server = SocketServer.TCPServer((HOST, PORT), DriverHandler)
  print('listening on %s:%d' % (HOST, PORT))
  server.serve_forever()
