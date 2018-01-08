#!/usr/bin/env python

from collections import namedtuple
import time

from display import Display
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


def Simulate(config):
  display = Display(config.length_m)
  client_info_list = []
  for i, client_spec in enumerate(config.clients):
    client_info = _ClientInfo(
        host=client_spec.host,
        port=client_spec.port,
        car=Car(position_m=i * config.start_spacing_m, velocity_m_s=0.0),
        connection=_FakeConnection(client_spec.host, client_spec.port))
    client_info_list.append(client_info)
  simulated_seconds = 0.0
  last_real_seconds = time.time()
  while simulated_seconds <= config.simulation_duration_s:
    for client_info in client_info_list:
      car = client_info.car
      resp = client_info.connection.Drive(
          DriveRequest(
              current=car,
              next=car,
              time_s=simulated_seconds,
              reward=0.0))
      car.velocity_m_s = min(config.max_velocity_m_s, max(0,
          car.velocity_m_s + resp.acceleration_m_s2 * config.time_step_s))
      car.position_m = (
          car.position_m +
          (car.velocity_m_s * config.time_step_s)) % config.length_m
    display.Update([client_info.car for client_info in client_info_list])
    simulated_seconds += config.time_step_s

    current_real_seconds = time.time()
    real_dt = current_real_seconds - last_real_seconds
    if real_dt < config.time_step_s:
      time.sleep(config.time_step_s - real_dt)
    last_real_seconds = current_real_seconds


if __name__ == '__main__':
  config = Config(
      length_m=500.0,
      start_spacing_m=1.0,
      time_step_s=1.0 / 24,
      simulation_duration_s=60.0,
      max_velocity_m_s=10.0)
  config.clients.add(host='localhost', port=8088)
  config.clients.add(host='localhost', port=8087)
  config.clients.add(host='localhost', port=8086)
  Simulate(config)
