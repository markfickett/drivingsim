import turtle


# http://colorbrewer2.org/#type=diverging&scheme=BrBG&n=8
PALETTE = (
  '#8c510a',
  '#01665e',
  '#bf812d',
  '#35978f',
  '#dfc27d',
  '#80cdc1',
  '#f6e8c3',
  '#c7eae5',
)

class Display(object):
  def __init__(self, length_m):
    self._length_m = length_m
    track_cursor = turtle.Turtle()
    self._radius = track_cursor.window_height() * 0.45

    track_cursor.reset()
    track_cursor.speed(0)  # no animation
    track_cursor.setpos(0, -self._radius)
    track_cursor.circle(self._radius)
    track_cursor.getscreen().tracer(0, 0)  # Turn off automatic updates.
    track_cursor.home()

    self._car_cursors = {}

  def _GetCarCursor(self, i):
    if i not in self._car_cursors:
      car_cursor = turtle.Turtle()
      car_cursor.speed(0)
      car_cursor.penup()
      car_cursor.color(PALETTE[i % len(PALETTE)])
      self._car_cursors[i] = car_cursor
    car_cursor = self._car_cursors[i]
    car_cursor.setheading(0)
    car_cursor.setpos(0, -self._radius)
    return car_cursor

  def Update(self, car_list):
    for i, car in enumerate(car_list):
      car_cursor = self._GetCarCursor(i)
      car_cursor.circle(self._radius, (car.position_m / self._length_m) * 360)
    car_cursor.getscreen().update()  # Force a rendering update.
