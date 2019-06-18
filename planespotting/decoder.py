from planespotting.identifiers import *


long_msg_bits = 112
short_msg_bits = 56

def getMsgLength(df):
    if df > 16:
        return long_msg_bits
    else:
        return short_msg_bits

def hexToDec(hexdec):
    dec = int(hexdec, 16)
    return bin(dec)[2:].zfill(56)

def getDF(frame):
    bin_frame = hexToDec(frame)
    df = int(bin_frame[0:5], 2)
    return df

def getTC(frame):
    data = frame[8:22]
    bin = hexToDec(data)
    if getMsgLength(getDF(frame)) == 112:
        return int(bin[0:5],2)
    else:
        return None

def decode(data):
    for frames in data["data"]:
        x = list()

        df = getDF(frames['adsb_msg'])
        tc = getTC(frames['adsb_msg'])

        decode_id = 0

        # grouping messages by df and tc, that can be decoded the same or share similar parts
        if identifier1(df, tc):
            decode_id = 1
            continue
        if identifier2(df, tc):
            decode_id = 2
            continue
        if identifier3(df, tc):
            decode_id = 3
            continue
        if identifier4(df, tc):
            decode_id = 4
            continue
        if identifier5(df, tc):
            decode_id = 5
            continue
        if identifier6(df, tc):
            decode_id = 6
            continue
        if identifier7(df, tc):
            decode_id = 7

        # todo more decoders needed, because many messages escape them!

        print(frames["id"], frames["timestamp"], df, tc, frames['adsb_msg'], decode_id)