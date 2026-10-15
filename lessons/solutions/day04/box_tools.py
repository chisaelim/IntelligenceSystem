def box_width(box):
    x1, y1, x2, y2 = box
    return x2 - x1


def box_area(box):
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)


if __name__ == "__main__":
    # This part runs only when you start THIS file, not when another file imports it.
    assert box_width((10, 10, 50, 40)) == 40
    assert box_area((10, 10, 50, 40)) == 1200
    print("box_tools self-test passed")
