
class Colour:
    ALPHA_CK = 255, 0, 255
    white = 255, 255, 255
    black = 20, 20, 40
    red = 255, 0, 0
    blue = 0, 0, 255
    path_blue = 26, 128, 178
    green = 0, 150, 0
    cyan = 20, 200, 200
    orange = 255, 160, 16

def check_disable(func):
    """Pythonic decorator that force function to do Nothing
    if disable is true"""
    def wrapper(*args, **kwargs):
        if args[0].disable:
            return
        return func(*args, **kwargs)
    return wrapper
