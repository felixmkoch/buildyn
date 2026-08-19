import weakref


class Checkpoint:

    def __init__(self, state, time, origin):

        self._state = state
        self._time = time
        self._origin = weakref.ref(origin)


    @property
    def state(self):
        return self._state


    @property
    def time(self):
        return self._time


    def belongs_to(self, instance) -> bool:

        return self._origin() is instance
