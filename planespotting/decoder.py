from planespotting.identifiers import *
from planespotting.utils import *


long_msg_bits = 112
short_msg_bits = 56


def getMsgLength(df):
    if df > 16:
        return long_msg_bits
    else:
        return short_msg_bits

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

def getICAO(frame):
    return frame[2:8]

def getAirbornePosition(frame):
    data = frame[8:22]
    bin = hexToDec(data)

    SS = int(bin[5:7],2)
    NICsb = int(bin[7],2)
    ALT = int(bin[8:20],2)
    T = int(bin[20],2)
    F = int(bin[21],2)
    LAT_CPR = int(bin[22:39],2)
    LON_CPR = int(bin[39:],2)

    return SS, NICsb, ALT, T, F, LAT_CPR, LON_CPR


def decode(data):
    #for id in range(len(data["data"])):
    for frames in data['data']:
        #frames = data["data"]
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

            SS, NICsb, ALT, T, F, LAT_CPR, LON_CPR = getAirbornePosition(frames['adsb_msg'])

            # filling in the now known values
            frames["ICAO"] = getICAO(frames['adsb_msg'])
            frames["SS"] = SS
            frames["NICsb"] = NICsb
            frames["ALT"] = ALT
            frames["T"] = T
            frames["F"] = F
            frames["LAT_CPR"] = LAT_CPR
            frames["LON_CPR"] = LON_CPR

            print(frames)
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

        #print(frames["id"], frames["timestamp"], df, tc, frames['adsb_msg'], decode_id)
