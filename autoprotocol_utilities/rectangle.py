from collections import namedtuple
try:
    reduce = reduce
except NameError:
    from functools import reduce  # py3k

# A column in a histogram
Column = namedtuple('Column', 'height x')
# An area under a histogram
Area = namedtuple('Area', 'width height x')
# A rectangle in a matrix/bitmap
Rect = namedtuple('Rect', 'width height x y')


def area(rect):
    """
    Computes geometrical area for Areas and Rects
    """
    return rect.width * rect.height


def area2rect(area, row_idx):
    """
    Converts an Area (no y coord) into a Rect. The y coord of the
    top left of the Rect is derived from the area height and the row_idx.
    """
    return Rect(width=area.width,
                height=area.height,
                x=area.x,
                y=row_idx-area.height+1)


def max_rectangle(mat, value=0):
    """Find height, width of the largest rectangle containing all `value`'s.
    For each row solve "Largest Rectangle in a Histrogram" problem [1]:
    [1]: http://blog.csdn.net/arbuckle/archive/2006/05/06/710988.aspx
    """
    row_idx = 0
    it = iter(mat)
    hist = [int(el == value) for el in next(it, [])]
    max_rect = area2rect(max_histogram_area(hist), row_idx)
    for row in it:
        row_idx += 1
        hist = [(1+h) if el == value else 0 for h, el in zip(hist, row)]
        max_rect_in_row = area2rect(max_histogram_area(hist), row_idx)
        max_rect = max(max_rect, max_rect_in_row, key=area)
    return max_rect


def max_histogram_area(histogram):
    """Find height, width of the largest rectangle that fits entirely under
    the histogram.
    Algorithm is "Linear search using a stack of incomplete subproblems" [1].
    [1]: http://blog.csdn.net/arbuckle/archive/2006/05/06/710988.aspx
    """
    stack = []
    top = lambda: stack[-1]
    max_area = Area(width=0, height=0, x=0)
    pos = 0  # current position in the histogram
    for pos, height in enumerate(histogram):
        start = pos
        while True:
            if not stack or height > top().height:
                stack.append(Column(height=height, x=start))  # push
            elif stack and height < top().height:
                col_height, col_x = stack.pop()
                stack_area = Area(width=pos-col_x, height=col_height, x=col_x)
                max_area = max(max_area, stack_area, key=area)
                start = col_x
                continue
            break  # height == top().height goes here

    pos += 1  # equivalent to pos = len(histogram)
    for height, start in stack:
        stack_area = Area(width=pos-start, height=height, x=start)
        max_area = max(max_area, stack_area, key=area)

    return max_area


def binary_list(wells, length=None):
    """Turns a list of indices into a binary list with list at
    indices that appear in the initial list set to 1, and 0
    otherwise. `wells` must be sorted, `length` is the length of
    the resulting list.

    .. code-block:: none

        [bnry for bnry in binary_list([1, 3, 5], length=7)]
        [0, 1, 0, 1, 0, 1, 0]

    """
    length = length or max(wells) + 1
    wells_ptr = 0
    for i in range(length):
        try:
            if wells[wells_ptr] == i:
                wells_ptr += 1
                yield 1
            else:
                yield 0
        except IndexError:
            yield 0


def chop_list(lst, chop_length, filler=None):
    """Chops a list into a list of lists. Used to generate a plate map
    corresponding to microplate layouts.
    """
    assert chop_length > 0
    ret = []
    row_idx = 0
    while True:
        # extract next chunk from input list
        row = lst[row_idx*chop_length:(row_idx+1)*chop_length]
        row_idx += 1
        row_len = len(row)

        # list length was integer multiple of chop_length
        if row_len == 0:
            return ret
        # still in the middle of the list
        elif row_len == chop_length:
            ret.append(row)
        # end of list, but last row needs filling up
        else:
            ret.append(row + [filler] * (chop_length - row_len))
            return ret

    return ret