def bytes_to_BCD(data:bytes, decimals:int = 0):
    """Decode from bytes a BCD number with decimal point"""
    res = 0
    for n, b in enumerate(reversed(data)):
        res += (b & 0x0F) * 10 ** (n * 2 - decimals)
        res += (b >> 4) * 10 ** (n * 2 + 1 - decimals)
    return res
