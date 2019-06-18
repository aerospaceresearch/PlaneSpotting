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

def df(frame):
    bin_frame = hexToDec(frame)
    df = int(bin_frame[0:5], 2)
    return df

def getTC(frame):
    data = frame[8:22]
    bin = hexToDec(data)
    if getMsgLength(df(frame)) == 112:
        return int(bin[0:5],2)
    else:
        return None

def decode(data):
    for frames in data["data"]:
        x = list()
        if identifier1(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier1")
            continue
        if identifier2(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier2")
            continue
        if identifier3(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier3")
            continue
        if identifier4(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier4")
            continue
        if identifier5(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier5")
            continue
        if identifier6(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier6")
            continue
        if identifier7(df(frames['adsb_msg']), getTC(frames['adsb_msg'])):
            print("Reaching decoder with identifier7")
