
#TODO: initialize with None, only average non-None items!
#      OR vary length of data array


class moving_average():
    """Like it sez."""
    def __init__(self, n_datapoints):

        self._moving_average_data = [None] * n_datapoints


    def update_moving_average(self, new_data_point):
        """return new average value"""

        # print(f"{data_list=} {new_data_point=}")
        new_list = self._moving_average_data[1:]
        new_list.append(new_data_point)

        # avg = sum(new_list) / len(new_list)
        total = 0
        np = 0
        for dp in new_list:
            if dp is not None:
                total += dp
                np += 1
        avg = total / np
        print(f"{new_list=} {avg=}")

        self._moving_average_data = new_list
        return avg


def test():

    ma = moving_average(5)

    print(f"{ma.update_moving_average(1)}")
    print(f"{ma.update_moving_average(2)}")
    print(f"{ma.update_moving_average(3)}")
    print(f"{ma.update_moving_average(4)}")
    print(f"{ma.update_moving_average(100)}")
    print(f"{ma.update_moving_average(100)}")

    print("done!")
    while True:
        pass
