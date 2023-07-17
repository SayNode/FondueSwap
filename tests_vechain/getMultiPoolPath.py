def makeFormattedHex(num):
    val="{0:#0{1}x}".format(num,8)
    return val

def append_hex(listOfHexs):
    
    for ind, hex in enumerate(listOfHexs):
        if type(hex)==int:
            hex = makeFormattedHex(hex)

        if ind==0:
            final_hex = listOfHexs[0]
        else:
            final_hex = final_hex + hex[2:]
    return final_hex