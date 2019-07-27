import os
import json
import math
import numpy as np
import gzip

def get_all_files(filename):
    '''
    This function returns the path to all the files present in a directory/folder.

    :param filename: Path to the directory/folder
    :type file: String (path)
    :return: File paths
    :rtype: Python list
    '''

    processing_files = []
    for root, dirs, files in os.walk(filename):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.isfile(filepath):
                #print("file", filepath)
                processing_files.append(filepath)

    return processing_files


def get_one_file(filename):
    '''
    To open a specific file for a code segment, this returns the single file path in an unit list.

    :param filename: Path to the specific file
    :type filename: String (path)
    :return: File path (singular)
    :rtype: Python list
    '''
    return [filename]


def is_binary(file):
    '''
    Checks if the file type is binary or text. It opens the file in text mode initially and and handles if an exception is thrown.
    If an exception occurs, then the file is non-binary and vice-versa.

    :param file: The file of which the type is to be checked.
    :type file: string
    :return: File type (text/binary)
    :rtype: Boolean
    '''
    try:
        with open(file, 'tr') as check_file:  # try opening file in text mode
            check_file.read()
            return False

    except:  # if false then file is non-binary
        return True


def hexToDec(hexdec):
    '''
    Converts hexadecimal code to binary of the length 4x of the hexadecimal string.

    :param hexdec: Hexadecimal String
    :type hexdec: string
    :return: Decimal string
    :rtype: String
    '''
    dec = int(hexdec, 16)
    bits = len(hexdec) * 4
    return bin(dec)[2:].zfill(bits)


def hexToBin(hexdec):
    '''
    Coverts hexadecimal code to 56 bit binary string.

    :param hexdec: Hexadecimal String
    :type hexdec: string
    :return: Decimal string
    :rtype: String
    '''
    dec = int(hexdec, 16)
    return bin(dec)[2:].zfill(56)

def hex2bin(hexstr):
    ''' Convert a hexdecimal string to binary string, with zero fillings.

    '''
    scale = 16
    num_of_bits = len(hexstr) * math.log(scale, 2)
    binstr = bin(int(hexstr, scale))[2:].zfill(int(num_of_bits))
    return binstr

def bin2np(binarystr):
    ''' Convert binary string to numpy array.

    :param binarystr: The message in binary
    :type binarystr: String
    :return: Numpy array
    :rtype: Numpy.ndarray
    '''
    return np.array([int(i) for i in binarystr])

def np2bin(npbin):
    """Convert a binary numpy array to string.

    :param npbin: Each bit of the message stored as an element in the array.
    :type npbin: Numpy.ndarray
    :return: Binary message in string
    :rtype: String
    """
    return np.array2string(npbin, separator='')[1:-1]

'''
Small type utility functions ends here
'''
def const_frame(): #Template for json structure for meta data

    json_frame = {
        "meta":{
            "file":None,
            "mlat_mode":None,
            "rec_start":None,
            "rec_end":None,
            "gs_lat":None,
            "gs_lon":None,
            "gs_alt":None,
            "gs_id":None,
            "gs_x":None,
            "gs_y":None,
            "gs_z":None,
            "gs_sampling_rate":None
        },
        "data":[]
    }

    return json_frame

def const_frame_data(): #This serves as a template for the json structure. Consists of only the data part

    json_frame = {
        "data":{
            "id":None,
            "is_repeated":None,
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
            #DF 21 & 5
            "squawk":None,
            "x": None,
            "y": None,
            "z": None,
            "time_propagation": None
        }
    }
    return json_frame

def create_folder(path):

    if not os.path.exists(path):
        os.makedirs(path)


def store_file(path, file, data):

    filename = file.split(os.sep)[-1].split(".")[0] + ".json"

    # create the folder
    create_folder(path)

    with open(path + os.sep + filename, "w") as outfile:
        json.dump(data, outfile, indent=4)


def store_file_jsonGzip(path, file, data):

    filename = file.split(os.sep)[-1].split(".")[0] + ".json.gz"

    # create the folder
    path = path+os.sep+file.split(os.sep)[1]
    create_folder(path)

    with gzip.open(path + os.sep + filename, 'wt', encoding="utf-8") as fout:
        json.dump(data, fout, indent=2)


def load_file_jsonGzip(filename):

    with gzip.GzipFile(filename, 'r') as fin:
        data = json.loads(fin.read().decode('utf-8'))

    return data

def load_json(filename):

    with open(filename, 'r') as fh:
        data = json.loads(fh.read())

    return data
