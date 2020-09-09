def recurse(level):
    print('recurse(%s)' % level)
    if level:
        recurse(level-1)
    return


def not_called():
    print('This function is never called.')

i = 5
i -= 2
recurse(i)

