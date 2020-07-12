def humanSize(size, level=0):
    if size >= 1024:
        humanSize(size/1024, level+1)

    return size, level;