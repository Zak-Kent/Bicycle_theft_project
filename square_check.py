import itertools
import logging

def square_check(sq_cords, x_coord, y_coord):
    """take a list of points (degx, degy, id) per point and an x, y cord and find the four points that make a square around x, y coord"""

    # make X coord postive and make a list of (x, y, id) tuples so itertools can make combinations 
    input_list = [((item[0] * -1), item[1], item[2]) for item in sq_cords]

    combs = itertools.combinations(input_list, 4)

    for item in combs: 
        points = sorted(item)               # order points by x, then by y
        (x1, y1, point11_id), (_x1, y2, point12_id), (x2, _y1, point21_id), (_x2, _y2, point22_id) = points

        if not x1 <= x_coord <= x2 or not y1 <= y_coord <= y2:
            #logging.debug("not a square")
            continue

        else:
            #logging.debug("square found")
            return (point11_id, point12_id, point21_id, point22_id) 


