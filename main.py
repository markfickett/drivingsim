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
    self._accel_m_s2 = -1.0

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
    for i, client_info in enumerate(client_info_list):
      car = client_info.car
      car_ahead = client_info_list[(i + 1) % len(client_info_list)].car
      req = DriveRequest(
          current=car,
          ahead=car_ahead,
          length_m=config.length_m,
          time_s=simulated_seconds,
          reward=0.0)
      resp = client_info.connection.Drive(req)

      car.velocity_m_s = min(config.max_velocity_m_s, max(0,
          car.velocity_m_s + resp.acceleration_m_s2 * config.time_step_s))

      # collisions
      ahead_pos_m = car_ahead.position_m
      while ahead_pos_m < car.position_m:
        ahead_pos_m += config.length_m
      car.position_m = (
          car.position_m +
          (car.velocity_m_s * config.time_step_s)) % config.length_m
      if car.position_m >= ahead_pos_m:
        car.velocity_m_s = 0.0
        car.position_m = ahead_pos_m - 1e-6
    simulated_seconds += config.time_step_s

    display.Update([client_info.car for client_info in client_info_list])

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
      max_velocity_m_s=50.0)
  for _ in xrange(20):
    config.clients.add(host='localhost', port=8088)
  Simulate(config)
