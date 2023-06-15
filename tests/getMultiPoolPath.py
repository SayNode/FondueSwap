def makeFormattedHex(num):
    val="{0:#0{1}x}".format(num,8)
    return val

def append_hex(listOfHexs):
    final_hex = listOfHexs[0]
    for ind, hex in enumerate(listOfHexs):
        if ind!=0:
            final_hex = final_hex + hex[2:]
    return final_hex

print(append_hex(["0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
                  makeFormattedHex(60),
                  '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                  makeFormattedHex(10),
                  '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                  makeFormattedHex(60),
                  '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599']))

print('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc200003cA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB4800000adAC17F958D2ee523a2206206994597C13D831ec700003c2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599')