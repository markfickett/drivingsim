#!/usr/bin/env python

from collections import namedtuple

from drivingsim_pb2 import Car
from drivingsim_pb2 import Client
from drivingsim_pb2 import Config
from drivingsim_pb2 import DriveRequest
from drivingsim_pb2 import DriveResponse

_ClientInfo = namedtuple('ClientInfo', ('host', 'port', 'car', 'connection'))


class _FakeConnection(object):
  def __init__(self, host, port):
    pass

  def Drive(self, request):
    return DriveResponse(acceleration_m_s2=9.8)


class _Display(object):
  def __init__(self, config):
    self.length_m = config.length_m

  def Update(self, car_list):
    pass


def Simulate(config):
  display = Display(config)
  client_info_list = []
  for client_spec in config.clients:
    client_info = _ClientInfo(
        host=client_spec.host,
        port=client_spec.port,
        car=Car(position_m=0.0, velocity_m_s=0.0),
        connection=_FakeConnection(client_spec.host, client_spec.port))
    client_info_list.append(client_info)
  for _ in xrange(int(config.simulation_duration_s / config.time_step_s)):
    for client_info in client_info_list:
      car = client_info.car
      resp = client_info.connection.Drive(
          DriveRequest(
              current=car,
              distance_to_next_m=10.0,
              reward=0.0))
      car.velocity_m_s = min(config.max_velocity_m_s, max(0,
          car.velocity_m_s + resp.acceleration_m_s2 * config.time_step_s))
      car.position_m = (
          car.position_m +
          (car.velocity_m_s * config.time_step_s)) % config.length_m
    display.update([client_info.car for client_info in client_info_list])


if __name__ == '__main__':
  config = Config(
      length_m=500,
      time_step_s=1.0,
      simulation_duration_s=60*60.0,
      max_velocity_m_s=100.0)
  config.clients.add(host='localhost', port=8088)
  Simulate(config)
