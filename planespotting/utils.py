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
def lat_index(lat_cpr_even, lat_cpr_odd):
    return math.floor((59 * lat_cpr_even) - (60*lat_cpr_odd) + 0.5)

def NL(lat): #this function calculates the number of longitude zones
    try:
        nz = 15 #Number of geographic latitude zones between equator and a pole
        a = 1 - math.cos(math.pi / (2 * nz))
        b = math.cos(math.pi / 180.0 * abs(lat)) ** 2
        nl = 2 * math.pi / (math.acos(1 - a/b))
        nl = int(nl)
        return nl

    except:
        return 1

def latitude(lat_cpr_even, lat_cpr_odd, t_even, t_odd): #Calculation of the latitude coordinate of the aircraft
    dlatEven = 6
    dlatOdd = 360/59
    cprEven = lat_cpr_even/131072
    cprOdd = lat_cpr_odd/131072
    j = lat_index(cprEven, cprOdd)
    latEven = dlatEven * (j % 60 + cprEven)
    latOdd = dlatOdd * (j % 59 + cprOdd)    #Calculation of relative latitudes

    if latEven >= 270:
        latEven -= 360

    if latOdd >= 270:
        latOdd -= 360

    if(NL(latEven) != NL(latOdd)):  #Confirmation of the validation of the calculated latitude, checks if latitude from both odd and evven frame lies in the same zone
        #exit("The positions are in different latitude zones")
        return 0
        #exit()
    if(t_even >= t_odd):
        return latEven

    else:
        return latOdd

def longitude(long_cpr_even, long_cpr_odd, t_even, t_odd, nl_lat):  #Calculation of longitude coordinate of the aircraft
    #if(NL(int(lat_even1, 2)) != NL(int(lat_odd1, 2))):
    #print(NL(10.2157745361328), NL(10.2162144547802))
    if(t_even > t_odd):
        ni = max(NL(nl_lat),1)
        dLon = 360 / ni
        cprEven1 = long_cpr_even/131072
        cprOdd1 = long_cpr_odd/131072
        m = math.floor(cprEven1 * (NL(nl_lat) - 1) - cprOdd1 * NL(nl_lat) + 0.5)
        lon =  dLon*(m % ni + cprEven1)


    elif(t_odd > t_even):
        ni = max(NL(nl_lat)-1,1)
        dLon = 360 / ni
        cprEven1 = long_cpr_even/131072
        cprOdd1 = long_cpr_odd/131072
        m = math.floor(cprEven1 * (NL(nl_lat) - 1) - cprOdd1 * NL(nl_lat) + 0.5) #Longitude index
        lon = dLon*(m%ni + cprOdd1)

    if(lon >= 180):                             #Coordinate correction, if it lies in the southern hemisphere
        return lon - 360

    else:
        return lon

'''
The calculation of both latitude and longitude is done
with respect to the newest frame received.

But, two frames are considered for calculation in order to
remove the ambiguity in the frames.
'''

def altitude(bin_alt):
    qBit = bin_alt[7]
    alt=bin_alt[0:7]+bin_alt[8:]
    altitude = int(alt, 2)
    if(int(qBit) == 1):  #Checks for the altitude multiplication unit, 0 = 100ft, 1 = 25ft
        return altitude * 25 - 1000
    else:
        return altitude * 100 - 1000
'''
Location determination functions ends hemisphere
For more information visit https://mode-s.org/decode/index.html
'''

def pos_local(latRef, lonRef, F, lat_cpr, lon_cpr):

    isEven = False

    if F == 0:
        isEven = True

    if isEven:
        dLat = 360/60
    else:
        dLat = 360/59

    lat_cpr = lat_cpr/131072
    j = math.floor(latRef/dLat) + math.floor(((latRef%dLat)/dLat) - lat_cpr + 0.5)
    lat = dLat * (j + lat_cpr)

    if isEven:
        if (NL(lat)) > 0:
            dLon = 360/NL(lat)
        else:
            dLon = 360
    else:
        if (NL(lat)-1) > 0:
            dLon = 360/(NL(lat)-1)
        else:
            dLon = 360

    lon_cpr = lon_cpr/131072
    m = math.floor(lonRef/dLon) + math.floor(((lonRef%dLon)/dLon) - lon_cpr + 0.5)
    lon = dLon * (m + lon_cpr)

    return lat, lon


def create_folder(path):

    if not os.path.exists(path):
        os.makedirs(path)


def store_file(path, file, data):

    filename = file.split(os.sep)[-1].split(".")[0] + ".json"

    # create the folder
    create_folder(path)

    with open(path + os.sep + filename, "w") as outfile:
        json.dump(data, outfile, indent=4)
