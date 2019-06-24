from planespotting.calculator import (calculate_position, convert_position, calculate_velocity)
from planespotting.utils import *
from planespotting.identifiers import *
import numpy as np


long_msg_bits = 112
short_msg_bits = 56


def get_MsgLength(df): #Returns the bit length of a message according to the type (df>16)
    if df > 16:
        return long_msg_bits
    else:
        return short_msg_bits
'''
All messages above df 16 are long messages
'''

def get_DF(frame):
    bin_frame = hexToDec(frame)
    df = int(bin_frame[0:5], 2)
    return df


def get_TC(frame):
    data = frame[8:22]
    bin = hexToDec(data)

    if get_MsgLength(get_DF(frame)) == 112:
        return int(bin[0:5],2)
    else:
        return None


def get_ICAO(frame):
    return frame[2:8]

def crc(msg, encoding=False):
    ''' Mode-S Cyclic Redundancy Check
    Detect if bit error occurs in the Mode-S message
    Args:
        msg (string): 28 bytes hexadecimal message string
        encoding (bool): True to encode the date only and return the checksum
    Returns:
        string: message checksum, or parity bits (encoder)
    '''

    # the polynominal generattor code for CRC [1111111111111010000001001]
    generator_poly = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,0,0,0,0,1,0,0,1])
    generatornumber = len(generator_poly)

    msgnpbin = bin2np(hex2bin(msg))

    if encoding:
        msgnpbin[-24:] = [0] * 24

    # loop all bits, except last 24 parity bits
    for i in range(len(msgnpbin) - 24):
        if msgnpbin[i] == 0:
            continue

        # perform XOR logic operation, when 1
        msgnpbin[i : i+generatornumber] = np.bitwise_xor(msgnpbin[i : i+generatornumber], generator_poly)

    # last 24 parity bits
    rest = np2bin(msgnpbin[-24:])
    return rest


def get_crcICAO(frame):
    c0 = int(crc(frame, encoding = True), 2)
    c1 = int(frame[-6:], 16)
    icao = '%06X' % (c0 ^ c1)
    return icao

def get_AirbornePosition(frame): #Extraction of position oriented data
    #print(frame)
    data = frame[8:22]
    bin = hexToDec(data)

    SS = int(bin[5:7],2)
    NICsb = int(bin[7],2)
    ALT = bin[8:20]
    T = int(bin[20],2)
    F = int(bin[21],2)
    LAT_CPR = int(bin[22:39],2)
    LON_CPR = int(bin[39:],2)

    return SS, NICsb, ALT, T, F, LAT_CPR, LON_CPR


def get_VelocityData(frame, subtype): #Extraction of velocity oriented data
    msg_bin = hexToDec(frame[8:22])
    if subtype == 1:
        IC = int(msg_bin[8], 2)
        RESV_A = int(msg_bin[9], 2)
        NAC =  int(msg_bin[10:13], 2)
        S_ew =  int(msg_bin[13], 2)
        V_ew =  int(msg_bin[14:24], 2)
        S_ns =  int(msg_bin[24], 2)
        V_ns =  int(msg_bin[25:35], 2)
        VrSrc =  int(msg_bin[35], 2)
        S_vr =  int(msg_bin[36], 2)
        Vr =  int(msg_bin[37:46], 2)
        RESV_B = int(msg_bin[46:48], 2)
        S_Dif = int(msg_bin[48], 2)
        Dif = int(msg_bin[49:56], 2)

        return IC, RESV_A, NAC, S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr, RESV_B, S_Dif, S_Dif, Dif

    elif subtype == 3:
        IC = int(msg_bin[8], 2)
        RESV_A = int(msg_bin[9], 2)
        NAC =  int(msg_bin[10:13], 2)
        S_hdg =  int(msg_bin[13], 2)
        Hdg =  int(msg_bin[14:24], 2)
        AS_t =  int(msg_bin[24], 2)
        AS =  int(msg_bin[25:35], 2)
        VrSrc =  int(msg_bin[35], 2)
        S_vr =  int(msg_bin[36], 2)
        Vr =  int(msg_bin[37:46], 2)
        RESV_B = int(msg_bin[46:48], 2)
        S_Dif = int(msg_bin[48], 2)
        Dif = int(msg_bin[49:56], 2)

        return IC, RESV_A, NAC, S_hdg, Hdg, AS_t, AS, VrSrc, S_vr, Vr, RESV_B, S_Dif, Dif


def get_SeenPlanes(data):

    all_seen_planes = []

    for frames in data["data"]:
        seen = 0
        for plane in all_seen_planes:

            if frames["ICAO"] == plane:
                seen = 1

        if seen == 0:
            all_seen_planes.append(frames["ICAO"])

    return all_seen_planes


def get_Callsign(callsign_bin):
    lookup_table = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"
    #print(msg, "Aircraft identifier", df, tc)
    #dat = frames['callsign_bin']
    callsign = ""
    for i in range(0, len(callsign_bin), 6):
        index = int(callsign_bin[i:i+6], 2)
        callsign += lookup_table[index]

    return callsign


'''
The calculation of both latitude and longitude is done
with respect to the newest frame received.

But, two frames are considered for calculation in order to
remove the ambiguity in the frames.
'''

def get_Squawk(frame):
    msg_bin = hexToDec(frame)
    C1 = msg_bin[19]
    A1 = msg_bin[20]
    C2 = msg_bin[21]
    A2 = msg_bin[22]
    C4 = msg_bin[23]
    A4 = msg_bin[24]
    # _ = mbin[25]
    B1 = msg_bin[26]
    D1 = msg_bin[27]
    B2 = msg_bin[28]
    D2 = msg_bin[29]
    B4 = msg_bin[30]
    D4 = msg_bin[31]

    str1 = int(A4+A2+A1, 2)
    str2 = int(B4+B2+B1, 2)
    str3 = int(C4+C2+C1, 2)
    str4 = int(D4+D2+D1, 2)

    return (str(str1) + str(str2) + str(str3) + str(str4))

def altitude(bin_alt):
    qBit = bin_alt[7]
    alt=bin_alt[0:7]+bin_alt[8:]
    altitude = int(alt, 2)
    if(int(qBit) == 1):  #Checks for the altitude multiplication unit, 0 = 100ft, 1 = 25ft
        return altitude * 25 - 1000
    else:
        return altitude * 100 - 1000



def decode(data):
    #for id in range(len(data["data"])):
    for frames in data['data']:

        df = get_DF(frames['adsb_msg'])
        tc = get_TC(frames['adsb_msg'])
        frames['df'] = df
        frames['tc'] = tc
        decode_id = 0

        #print(frames['adsb_msg'])
        # grouping messages by df and tc, that can be decoded the same or share similar parts
        if identifier1(df, tc):
            decode_id = 1
            frames['callsign'] = get_Callsign(hexToDec(frames['adsb_msg'])[40:88])
            frames['parity'] = frames['adsb_msg'][-6:]
            continue

        if identifier2(df, tc):
            decode_id = 2
            continue

        if identifier3(df, tc):
            decode_id = 3

            SS, NICsb, ALT, T, F, LAT_CPR, LON_CPR = get_AirbornePosition(frames['adsb_msg'])
            frames['parity'] = frames['adsb_msg'][-6:]
            # filling in the now known values
            frames["ICAO"] = get_ICAO(frames['adsb_msg'])
            frames["SS"] = SS
            frames["NICsb"] = NICsb
            frames["ALT"] = ALT
            frames["T"] = T
            frames["F"] = F
            frames["LAT_CPR"] = LAT_CPR
            frames["LON_CPR"] = LON_CPR
            frames["isBaroAlt"] = 1
            frames['altitude'] = altitude(ALT)

            #print(frames)
            continue

        if identifier4(df, tc):
            decode_id = 4
            subtype = int(hexToDec(frames['adsb_msg'][8:22])[5:8], 2)
            frames["ICAO"] = get_ICAO(frames['adsb_msg'])
            frames['parity'] = frames['adsb_msg'][-6:]
            if subtype == 1:
                IC, RESV_A, NAC, S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr, RESV_B, S_Dif, S_Dif, Dif = get_VelocityData(frames['adsb_msg'], subtype)
                frames['Subtype'] = subtype
                frames["IC"] = IC
                frames["RESV_A"] = RESV_A
                frames["NAC"] =  NAC
                frames["S_ew"] =  S_ew
                frames["V_ew"] =  V_ew
                frames["S_ns"] =  S_ns
                frames["V_ns"] =  V_ns
                frames["VrSrc"] =  VrSrc
                frames["S_vr"] =  S_vr
                frames["Vr"] =  Vr
                frames["RESV_B"] = RESV_B
                frames["S_Dif"] = S_Dif
                frames["Dif"] = Dif

            elif subtype == 3:
                IC, RESV_A, NAC, S_hdg, Hdg, AS_t, AS, VrSrc, S_vr, Vr, RESV_B, S_Dif, Dif = get_VelocityData(frames['adsb_msg'], subtype)
                frames['Subtype'] = subtype
                frames["IC"] = IC
                frames["RESV_A"] = RESV_A
                frames["NAC"] =  NAC
                frames["S_hdg"] =  S_hdg
                frames["Hdg"] = Hdg
                frames["AS_t"] =  AS_t
                frames["AS"] =  AS
                frames["VrSrc"] =  VrSrc
                frames["S_vr"] =  S_vr
                frames["Vr"] =  Vr
                frames["RESV_B"] = RESV_B
                frames["S_Dif"] = S_Dif
                frames["Dif"] = Dif
            #print(frames)
            continue

        if identifier5(df, tc):
            decode_id = 5
            continue

        if identifier6(df, tc):
            decode_id = 6
            adsb_msg = frames['adsb_msg']
            frames['ICAO'] = get_ICAO(adsb_msg)
            adsb_msg_data = hexToDec(adsb_msg[8:22])
            ver = int(adsb_msg_data[40:43], 2)
            frames['parity'] = frames['adsb_msg'][-6:]


            frames['stype_code'] = int(adsb_msg_data[5:8], 2)
            frames['sccc'] = int(adsb_msg_data[8:20], 2)
            frames['lw_codes'] = int(adsb_msg_data[20:24], 2)
            frames['op_mc'] = int(adsb_msg_data[24:40], 2)
            frames['ver'] = ver
            frames['NIC'] = int(adsb_msg_data[43], 2)
            frames['NACp'] = int(adsb_msg_data[44:48], 2)
            frames['SIL'] = int(adsb_msg_data[50:52], 2)
            frames['NIC_bit'] = int(adsb_msg_data[52], 2)
            frames['HRD'] = int(adsb_msg_data[53], 2)
            frames['resv_op'] = int(adsb_msg_data[54:56], 2)

            if ver == 1:
                frames['BAQ'] = int(adsb_msg_data[48:50], 2)

            elif ver == 2:
                frames['GVA'] = int(adsb_msg_data[48:50], 2)
                frames['SIL_bit'] = int(adsb_msg_data[54], 2)

            continue

        if identifier7(df, tc):
            adsb_msg_bin = hexToDec(frames['adsb_msg'][8:22])
            frames['ICAO'] = get_crcICAO(frames['adsb_msg'])
            bds1 = int(adsb_msg_bin[:4], 2)
            bds2 = int(adsb_msg_bin[4:8], 2)
            frames['parity'] = frames['adsb_msg'][-6:]

            if bds1 == 2 and bds2 == 0:
                frames['callsign'] = get_Callsign(hexToDec(frames['adsb_msg'])[40:88])
                #print(frames)
                #exit(frames)
            if bds1 == 4 and bds2 == 0: #Not tested due to lack of frames
                frames['mcp_alt'] = int(adsb_msg_bin[1:13], 2) * 16
                frames['fms_alt'] = int(adsb_msg_bin[14:26], 2) * 16
                frames['baro_set'] = int(adsb_msg_bin[27: 39], 2) * 0.1 + 800
                frames['VNAV_state'] = int(adsb_msg_bin[48], 2)
                frames['Alt_hold_state'] = int(adsb_msg_bin[49], 2)
                frames['Apr_state'] = int(adsb_msg_bin[50], 2)
                frames['tgt_alt_source'] = adsb_msg_bin[54:56] #values are 00 01 10 11, so no conversion

            if bds1 == 5 and bds2 == 0:
                frames['roll_angle'] = (int(adsb_msg_bin[2:11], 2) * (45.0/256.0) if adsb_msg_bin[1] == 0 else int(adsb_msg_bin[2:11], 2) - 512) * (45.0/256.0)
                frames['true_track_angle'] = (int(adsb_msg_bin[13:23], 2) * (90.0/512.0) if adsb_msg_bin[12] == 0 else int(adsb_msg_bin[13:23], 2) - 512) * (90.0/512.0)
                frames['ground_speed'] = int(adsb_msg_bin[24:34], 2) * 2
                frames['track_angle_rate'] = (int(adsb_msg_bin[36:45], 2) * (8.0/256.0) if adsb_msg_bin[35] == 0 else int(adsb_msg_bin[36:45], 2) - 512) * (8.0/256.0)
                frames['TAS'] = int(adsb_msg_bin[46:56], 2) * 2

            if bds1 == 6 and bds2 == 0:
                frames['mag_hdg'] = (int(adsb_msg_bin[2:12], 2) * (90.0/512.0) if adsb_msg_bin[1] == 0 else int(adsb_msg_bin[2:12], 2) - 512) * (90.0/512.0)
                frames['IAS'] = int(adsb_msg_bin[13:23], 2) * 1
                frames['mach'] = int(adsb_msg_bin[24:34], 2) * (2.048/512)
                frames['baro_alt_rate'] = (int(adsb_msg_bin[36:45], 2) * (32) if adsb_msg_bin[35] == 0 else int(adsb_msg_bin[36:46], 2) - 512) * (32)
                frames['inertial_alt_rate'] = (int(adsb_msg_bin[47:56], 2) * (32) if adsb_msg_bin[46] == 0 else int(adsb_msg_bin[47:56], 2) - 512) * (32)
            decode_id = 7
            if frames['df'] == 21:

                frames['squawk'] = get_Squawk(frames['adsb_msg'])

        '''
        Decoding 56 bit msgs from hemisphere
        '''

        if identifier8(frames['df'], frames['tc']):

            frames['squawk'] = get_Squawk(frames['adsb_msg'])
            #exit(frames)
        # todo more decoders needed, because many messages escape them!


    # finding all the already available and seen ICAO addresses
    data = calculate_position(get_SeenPlanes(data), data)
    data = convert_position(data)
    data = calculate_velocity(data)

    return data
