
#TODO: initialize with None, only average non-None items!
#      OR vary length of data array


class moving_average():
    """Like it sez."""
    def __init__(self, n_datapoints):

        self._n_datapoints = n_datapoints
        self._moving_average_data = []


    def update_moving_average(self, new_data_point):
        """return new average value"""

        if len(self._moving_average_data) == self._n_datapoints:
            self._moving_average_data = self._moving_average_data[1:]
        self._moving_average_data.append(new_data_point)

        avg = sum(self._moving_average_data) / len(self._moving_average_data)

        # print(f"{self._moving_average_data=} + {new_data_point=} -> {new_list=}, {avg=}")
        print(f"  + {new_data_point=} -> {self._moving_average_data=}, {avg=}")

        return avg


def test():

    ma = moving_average(4)

    print(f"{ma.update_moving_average(1)}")
    print(f"{ma.update_moving_average(2)}")
    print(f"{ma.update_moving_average(3)}")
    print(f"{ma.update_moving_average(4)}")
    print(f"{ma.update_moving_average(100)}")
    print(f"{ma.update_moving_average(100)}")
    print(f"{ma.update_moving_average(100)}")
    print(f"{ma.update_moving_average(100)}")

    print("done!")
    while True:
        pass
