from planespotting.calculator import (calculate_position, convert_position, calculate_velocity)
from planespotting.utils import *
from planespotting.identifiers import *
from planespotting.multilateration import *
import numpy as np


long_msg_bits = 112
short_msg_bits = 56


def get_MsgLength(df):
    '''
    Returns the bit length of a message according to the type (df>16)

    :param df: Downlink format
    :type df: Integer
    :return: Length of messages
    :rtype: Integer
    '''
    if df > 16:
        return long_msg_bits
    else:
        return short_msg_bits
'''
All messages above df 16 are long messages
'''

def get_DF(frame):
    '''
    This function returns the Downlink Format of any ads-b message present in the stream

    :param frame: The 56/112 bit ads-b message
    :type frame: String
    :return: Downlink format of 'frame'
    :rtype: Integer
    '''
    bin_frame = hexToDec(frame)
    df = int(bin_frame[0:5], 2)
    return df


def get_TC(frame):
    '''
    Extraction of Type code from 112 bit ads-b messages

    :param frame: 112 bit ads-b message
    :type frame: String
    :return: It returns the integer equivalent of the first 4 bits of the ads-b message block
    :rtype: Integer
    '''
    data = frame[8:22]
    bin = hexToDec(data)

    if get_MsgLength(get_DF(frame)) == 112:
        return int(bin[0:5],2)
    else:
        return None


def get_ICAO(frame):
    '''
    Extracts the ICAO of Downlink Format 11, 17 & 18 messages only

    :param frame: ADS-b message with DF 11, 17 or 18
    :type frame: String
    :return: The icao 24-bit address in hexadecimal format
    :rtype: String
    '''
    return frame[2:8]

def get_gray2alt(codestr):
    '''
    This function converts gray code to altitude
    :param codestr: Binary of the altitude code cut from the ads-b frame
    :type codestr: String
    :return: Altitude
    :rtype: Integer
    '''
    gc500 = codestr[:8]
    n500 = gray2int(gc500)

    # in 100-ft step must be converted first
    gc100 = codestr[8:]
    n100 = gray2int(gc100)

    if n100 in [0, 5, 6]:
        return None

    if n100 == 7:
        n100 = 5

    if n500%2:
        n100 = 6 - n100

    alt = (n500*500 + n100*100) - 1300
    return alt

def gray2int(graystr):
    """Convert greycode to binary.

    :param graystr: String to be converted
    :type graystr: String
    :return: Binary equivelnt
    :rtype: Integer
    """
    num = int(graystr, 2)
    num ^= (num >> 8)
    num ^= (num >> 4)
    num ^= (num >> 2)
    num ^= (num >> 1)
    return num

def crc(msg, encoding=False):
    ''' Mode-S Cyclic Redundancy Check
    Detect if bit error occurs in the Mode-S message

    :param msg: 28 bytes hexadecimal message string
    :param encoding: True to encode the date only and return the checksum
    :type msg: String
    :type encoding: Boolean
    :return: message checksum, or parity bits (encoder)
    :rtype: String
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
    '''
    Extracts the ICAO of Downlink Format 0, 4, 5, 16, 20 & 21 messages only

    :param frame: ADS-b message with DF 0, 4, 5, 16, 20 or 21
    :type frame: String
    :return: The icao 24-bit address in hexadecimal format
    :rtype: String
    '''
    c0 = int(crc(frame, encoding = True), 2)
    c1 = int(frame[-6:], 16)
    icao = '%06X' % (c0 ^ c1)
    return icao

def get_AirbornePosition(frame): #Extraction of position oriented data
    '''
    This function cuts and converts the binary data into its equivalent integer.
    The data cut consists of the variables required for position determination.

    :param frame: 112bit DF 17/18 and tc:9-18 ADS-B message
    :type frame: String
    :return: SS(integer): Surveillance status,
        NICsb(integer) : NIC supplement-B,
        ALT(integer):Altitude,
        T(integer):Time,
        F(integer):CPR odd/even frame flag,
        LAT_CPR(integer):Latitude in CPR format,
        LON_CPR(integer):Longitude in CPR format
    :rtype: Integer
    '''
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


def get_VelocityData(frame, subtype): #Extraction of velocity oriented
    '''
    This function cuts and converts the binary data into its equivalent integer.
    The data cut consists of the variables required for veocity and heading calculation.
    Args:
        frame(string): 112bit DF 17/18 and tc:9-18 ADS-B message
    Returns:
        IC(integer) : Intent change flag
        RESV_A(integer) : Reserved-A
        NAC(integer) : Velocity uncertainty (NAC)
        S_ew(integer) : East-West velocity sign
        V_ew(integer) : East-West velocity
        S_ns(integer) : North-South velocity sign
        V_ns(integer) : North-South velocity
        VrSrc(integer) : Vertical rate source
        S_vr(integer) : Vertical rate sign
        Vr(integer) : Vertical rate
        RESV_B(integer) : Reserved-B
        S_Dif(integer) : Diff from baro alt, sign
        Dif(integer) : Diff from baro alt

    When subtype = 3
    Returns:
            IC(integer) : Intent change flag
            RESV_A(integer) : Reserved-A
            NAC(integer) : Velocity uncertainty (NAC)
            S_hdg(integer) : Heading status
            Hdg(integer) : Heading (proportion)
            AS_t (integer) : Airspeed Type
            AS (integer) : Airspeed
            VrSrc (integer) : Vertical rate source
            S_vr (integer) : Vertical rate sign
            Vr(integer) : Vertical rate
            RESV_B (integer) : Reserved-B
            S_Dif (integer) : Difference from baro alt, sign
            Dif(integer) : Difference from baro alt

    '''
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

        return IC, RESV_A, NAC, S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr, RESV_B, S_Dif, Dif

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

def get_altCode(frame):
    msg_bin = hexToDec(frame)
    mbit = msg_bin[25]
    qbit = msg_bin[27]

    if mbit == "0":
        if qbit == "1":
            vbin = msg_bin[19:25] + msg_bin[26] + msg_bin[28:32]
            alt_code = int(vbin, 2) * 25 - 1000
        else:
            C1 = msg_bin[19]
            A1 = msg_bin[20]
            C2 = msg_bin[21]
            A2 = msg_bin[22]
            C4 = msg_bin[23]
            A4 = msg_bin[24]
            B1 = msg_bin[26]
            B2 = msg_bin[28]
            D2 = msg_bin[29]
            B4 = msg_bin[30]
            D4 = msg_bin[31]

            graystr =  D2 + D4 + A1 + A2 + A4 + B1 + B2 + B4 + C1 + C2 + C4
            alt_code = get_gray2alt(graystr)
    else:
        vbin = msg_bin[19:25] + msg_bin[26:31]
        alt_code = int(int(vbin, 2) * 3.28084)

    return alt_code

def decode(data):
    #for id in range(lendata["data"])):
    frame_check = []
    for frames in data['data']:

        if frames['adsb_msg'] not in frame_check:
            frame_check.append(frames['adsb_msg'])
        else:
            frames['is_repeated'] = 1
            #continue

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
                IC, RESV_A, NAC, S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr, RESV_B, S_Dif, Dif = get_VelocityData(frames['adsb_msg'], subtype)
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
            decode_id = 7

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
                #mcpalt always 32768 and baro 800mb
                #got in file 1, 4 frames - only from light

            if bds1 == 5 and bds2 == 0:
                frames['roll_angle'] = int(adsb_msg_bin[2:11], 2) * (45.0/256.0) if adsb_msg_bin[1] == "0" else (int(adsb_msg_bin[2:11], 2) - 512) * (45.0/256.0)
                frames['true_track_angle'] = int(adsb_msg_bin[13:23], 2) * (90.0/512.0) if adsb_msg_bin[12] == "0" else (int(adsb_msg_bin[13:23], 2) - 512) * (90.0/512.0)
                frames['ground_speed'] = int(adsb_msg_bin[24:34], 2) * 2
                frames['track_angle_rate'] = int(adsb_msg_bin[36:45], 2) * (8.0/256.0) if adsb_msg_bin[35] == "0" else (int(adsb_msg_bin[36:45], 2) - 512) * (8.0/256.0)
                frames['TAS'] = int(adsb_msg_bin[46:56], 2) * 2
                #found in file 1, only 1 frame
            if bds1 == 6 and bds2 == 0:
                frames['mag_hdg'] = int(adsb_msg_bin[2:12], 2) * (90.0/512.0) if adsb_msg_bin[1] == "0" else (int(adsb_msg_bin[2:12], 2) - 1024) * (90.0/512.0)
                frames['IAS'] = int(adsb_msg_bin[13:23], 2) * 1
                frames['mach'] = int(adsb_msg_bin[24:34], 2) * (2.048/512)
                frames['baro_alt_rate'] = int(adsb_msg_bin[36:45], 2) * (32) if adsb_msg_bin[35] == "0" else (int(adsb_msg_bin[36:46], 2) - 512) * (32)
                frames['inertial_alt_rate'] = int(adsb_msg_bin[47:56], 2) * 32 if adsb_msg_bin[46] == "0" else (int(adsb_msg_bin[47:56], 2)-512)*32
                #found lot of frames in 1

            if frames['df'] == 20:
                frames['altitude'] = get_altCode(frames['adsb_msg'])
                #exit(frames)

            if frames['df'] == 21:

                frames['squawk'] = get_Squawk(frames['adsb_msg'])

        '''
        Decoding 56 bit msgs from here
        '''

        if identifier8(frames['df'], frames['tc']):
            frames['ICAO'] = get_crcICAO(frames['adsb_msg'])
            frames['squawk'] = get_Squawk(frames['adsb_msg'])

        if identifier9(frames['df'], frames['tc']):
            frames['ICAO'] = get_crcICAO(frames['adsb_msg'])

        if identifier10(frames['df'], frames['tc']):
            frames['ICAO'] = get_crcICAO(frames['adsb_msg'])
            frames['altitude'] = get_altCode(frames['adsb_msg'])

        if identifier11(frames['df'], frames['tc']):
            frames['ICAO'] = get_crcICAO(frames['adsb_msg'])

        #Currently decoding only icao from DF0, 4, 5, 16, need more reading on what more can we decode

        # todo more decoders needed, because many messages escape them!


    # finding all the already available and seen ICAO addresses
    data = calculate_position(get_SeenPlanes(data), data)
    data = convert_position(data)
    data = calculate_signalpropagationtime(data)
    data = calculate_velocity(data)

    return data
