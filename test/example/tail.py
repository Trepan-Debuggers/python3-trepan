import os, sys

# Implement a function that works like tail.
# tail -n 10 file.txt
# will return last 10 lines from the file.

# Issues:
#   Q: do we have to worry about -f?
#   A: No.
#   Q: what do we do if tail count is greater than lines of file?
#   A: give entire file
#   Q: how do we handle if last line doesn't contain a \n?
#   A: treat it like it has \n

# Algorithm idea:
#   go to end keeping track of the i-th
#   from the end line end, where i goes from 0 to n;
#   n is the number of lines to tail.
#   Then seek to that position and print the remaining bytes.
#
# Time Complexity:
#   Let m be the size of the file and n size of the output
#   and k be the blocksize
#   Complexity is O(min(m,n)/k) since we may have to read and print the entire file
# Space Complexity:
#   O(min(m, k))

def get_tail_start(path, count, blocksize):
    """Return the position of where to start the tail listing.
    This is \n positions from the end of the path. None
    """
    # seek to end - blocksize
    file_size = os.stat(path).st_size
    seek_position = file_size
    # print(seek_position)
    remaining = count+1
    at_end = False
    pos = -1
    first_time = True
    with open(path) as fd:
        while remaining > 0 and seek_position >= 0 and not at_end:
            seek_position -= blocksize
            if seek_position < 0: seek_position = 0
            fd.seek(seek_position)
            block = fd.read(blocksize)
            if first_time:
                if block[-1:] != "\n": remaining -= 1
                first_time = False
            at_end = len(block) < blocksize
            pos, remaining = find_line_end(block, remaining)
    if pos is None: pos = -1
    # print(seek_position + pos + 1)
    return seek_position + pos + 1


def find_line_end(block, remaining):
    """Search backwards from block for at most *remaining* \n's
    and return tuple [position, 0] if found in this block or
    [None, remaining] if we have more to go"""
    last_position = len(block)
    while remaining != 0:
        position = block.rfind("\n", 0, last_position)
        if position == -1: return [None, remaining]
        remaining -= 1
        last_position = position
    return [last_position, 0]

def print_tail(path, pos, blocksize):
    with open(path) as fd:
        fd.seek(pos)
        block = fd.read(blocksize)
        while len(block) > 0:
            if sys.version_info[0] < 3:
                os.write(sys.stdout.fileno(), block)
            else:
                os.write(sys.stdout.fileno(), bytes(block, 'UTF-8'))
            block = fd.read(blocksize)

if __name__ == '__main__':
    count = 5
    path = __file__
    # path = './test.txt'
    # blocksize = 10000
    # pos = get_tail_start(path, count, blocksize)
    # print_tail(path, pos, blocksize)
    # print('-----')
    for blocksize in [5, 100, 100000]:
        for count in range(5):
            pos = get_tail_start(path, count, blocksize)
            print('-------------------- %d' % count)
            print_tail(path, pos, blocksize)
            print('====================')
