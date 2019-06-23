import os
import math
import json

def get_all_files(filename):

    processing_files = []
    for root, dirs, files in os.walk(filename):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.isfile(filepath):
                #print("file", filepath)
                processing_files.append(filepath)

    return processing_files


def get_one_file(filename):
    return [filename]


def is_binary(file):
    try:
        with open(file, 'tr') as check_file:  # try opening file in text mode
            check_file.read()
            return False

    except:  # if false then file is non-binary
        return True


def hexToDec(hexdec):
    dec = int(hexdec, 16)
    return bin(dec)[2:].zfill(56)


def hexToBin(hexdec):
    dec = int(hexdec, 16)
    return bin(dec)[2:].zfill(56)
'''
Small type utility functions ends here
'''
def const_frame(): #Template for json structure for meta data

    json_frame = {
        "meta":{
            "file":None,
            "mlat_mode":None,
            "gs_lat":None,
            "gs_lon":None,
            "gs_alt":None,
        },
        "data":[]
    }

    return json_frame

def const_frame_data(): #This serves as a template for the json structure. Consists of only the data part

    json_frame = {
        "data":{
            "id":None,
            "raw":None,
            "adsb_msg":None,
            "timestamp":None,
            "SamplePos":None,
            "df":None,
            "tc":None,
            #"callsign_bin":None,
            "capability":None,
            "ICAO":None,
            "parity":None,
            "SS":None,
            "NICsb":None,
            "ALT": None,
            "T":None,
            "F":None,
            "LAT_CPR":None,
            "LON_CPR":None,
            "latitude":None,
            "longitude":None,
            "altitude":None,
            "isBaroAlt":None,
            "callsign":None,
            #Airborne velocity Subtype 1data
            "Subtype":None,
            "IC":None,
            "RESV_A":None,
            "NAC":None,
            "S_ew":None,
            "V_ew":None,
            "S_ns":None,
            "V_ns":None,
            "VrSrc":None,
            "S_vr":None,
            "Vr":None,
            "RESV_B":None,
            "S_Dif":None,
            "Dif":None,
            "isGspeed":None,
            "velocity":None, #result
            "vert_rate":None, #result
            "heading":None,    #result
            #Subtype 3
            "S_hdg":None,
            "Hdg":None,
            "AS_t":None,
            "AS":None,
            #Operation status
            "stype_code":None,
            "sccc":None,
            "lw_codes":None,
            "op_mc":None,
            "ver":None,
            "NIC":None,
            "NACp":None,
            "BAQ":None,
            "SIL":None,
            "NIC_bit":None,
            "HRD":None,
            "resv_op":None,
            #version 2
            "GVA":None,
            "SIL_bit":None,
            #Enhanced MODE-S
            "bds_1":None,
            "bds_2":None,
            "mcp_alt":None,
            "fms_alt":None,
            "baro_set":None,
            "VNAV_state":None,
            "Alt_hold_state":None,
            "Apr_state":None,
            "tgt_alt_source":None,
            #BDS5, 0
            "roll_angle":None,
            "true_track_angle":None,
            "ground_speed":None,
            "track_angle_rate":None,
            "TAS":None,
            # BDS 6, 0
            "mag_hdg":None,
            "IAS":None,
            "mach":None,
            "baro_alt_rate":None,
            "inertial_alt_rate":None,

            #"prev_lat":None,
            #"prev_long":None,
            #"isLocalUni":None, #If the location is calculated is locally unambiguous (1 frame method)
            # multilateration
            "x": None,
            "y": None,
            "z": None
        }
    }
    return json_frame


'''
Below are the functions for location determination
'''
#calculation of latitude index, which is mostly 8

'''
Location determination functions ends hemisphere
For more information visit https://mode-s.org/decode/index.html
'''
def create_folder(path):

    if not os.path.exists(path):
        os.makedirs(path)


def store_file(path, file, data):

    filename = file.split(os.sep)[-1].split(".")[0] + ".json"

    # create the folder
    create_folder(path)

    with open(path + os.sep + filename, "w") as outfile:
        json.dump(data, outfile, indent=4)
