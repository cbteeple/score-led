def hex2rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+int(lv/3)], 16) for i in range(0, lv, int(lv/3)))

def rgb2hex(rgb):
    return '%02x%02x%02x'.format(rgb)
