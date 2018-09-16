
def is_integer(var):
    try:
        complex(var)
    except ValueError:
        return False

    return True
