
def is_intersection(xmin_a: int, xmax_a: int, ymin_a: int, ymax_a: int, xmin_b: int, xmax_b: int, ymin_b: int, ymax_b: int) -> bool:
    intersection_flag = True

    minx = max(xmin_a, xmin_b)
    miny = max(ymin_a, ymin_b)

    maxx = min(xmax_a, xmax_b)
    maxy = min(ymax_a, ymax_b)

    if minx > maxx or miny > maxy:
        intersection_flag = False

    return intersection_flag

