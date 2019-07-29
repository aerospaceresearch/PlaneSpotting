from planespotting.identifiers import *
from planespotting.utils import *
import math
import numpy as np

#All imports end here
'''
Beginning of position calculation functions
'''
def lat_index(lat_cpr_even, lat_cpr_odd):
    '''
    Used to calculate the latitude index using the odd and even frame latitudes.

    :param lat_cpr_even: The latitude data from an even frame
    :param lat_cpr_odd: The longitude data from the odd frame with the same icao as the even frame
    :type lat_cpr_even: Float
    :type lat_cpr_odd: Float
    :return: Latitude index
    :rtype: Float
    '''
    return math.floor((59 * lat_cpr_even) - (60*lat_cpr_odd) + 0.5)

def NL(lat): #this function calculates the number of longitude zones
    '''
    This function returns the number of latitude zones from the latitude angle. The returned value lies inbetween [1, 59]

    :param lat: The latitude angle
    :type lat: Float
    :return: Number of latitude zones
    :rtype: Integer

    '''
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
    '''
    Calculation of the latitude of a given aircraft with a set of successively received odd and even pair of frames.
    This type of calculation is also known as 'Globally unambigous position calculation' in which you need an odd and even frames from the same
    icao received one after the another.
    The order at which the frames at which the frames were received also determines the methodology of the calculation.
    For more info: https://mode-s.org/decode/adsb/airborne-position.html

    :param lat_cpr_even: Latitude data from the even frame
    :param lat_cpr_odd: Latitude data from the odd frame
    :param t_even: Time/Sample Position of the even message in the recording
    :param t_odd: Time/Sample Position of the odd message in the recording
    :type lat_cpr_even: Float
    :type lat_cpr_odd: Float
    :type t_even: Long
    :type t_odd: Long
    :return: Latitude in degrees
    :rtype: Float
    '''
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
        return 0
    if(t_even >= t_odd):
        return latEven

    else:
        return latOdd

def longitude(long_cpr_even, long_cpr_odd, t_even, t_odd, nl_lat):  #Calculation of longitude coordinate of the aircraft
    '''
    Calculation of the Longitude coordinate with the same set of successively received odd and even pair of frames as used in the latitude() function.
    In this function, the order of the odd and even frames is considered for calculation

    :param long_cpr_even: Latitude data from the even frame
    :param long_cpr_odd: Latitude data from the odd frame
    :param t_even: Time/Sample Position of the even message in the recording
    :param t_odd: Time/Sample Position of the odd message in the recording
    :type long_cpr_even: Float
    :type long_cpr_odd: Float
    :type t_even: Long
    :type t_odd: Long
    :return: Longitude in degrees
    :rtype: Float

    '''

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
functions for two frame methods ends here
'''


def pos_local(latRef, lonRef, F, lat_cpr, lon_cpr):
    '''
    Calculation of position using one frame only or 'Locally unambigous position calculation'> It uses a reference location to remove the ambiguity in the frame.

    :param latRef: Reference latitude (ground station or previous known location)
    :param lonRef: Reference longitude (ground station or previous known location)
    :param F: Odd/Even bit of the frame
    :param lat_cpr: Latitude data from the frame
    :param lon_cpr: Longitude data from the frame
    :type latRef: Float
    :type lonRef: Float
    :type F: Integer
    :type lat_cpr: Long
    :type lon_cpr: Long
    :return: Latitide, longitude
    :rtype: Float, Float

    '''

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

'''
all position calculation functions end here.
'''

def get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global):

    '''
    Calculation of the mean of all the decoded positions (lat, lon). Returns the mean (lat, lon)
    This mean(lat, lon) is used as the reference position for the locally unambigous method.

    :param data: Contains all the frames seen in the recording.
    :param relevant_planes_id: List containing frames which contain airborne position data.
    :param hit_counter_global: Number of frames considered during average calculation at each iteration.
    :param latitudeMean_global: Mean of all calculated latitudes which gets updated after each iteration.
    :param longitudeMean_global: Mean of all calculated longitudes which gets updated after each iteration.
    :type data: Python List
    :type relevant_planes_id: Python List
    :type hit_counter_global: Long
    :type latitudeMean_global: Float
    :type longitudeMean_global: Float
    :return: Latitude, Longitude
    :rtype: Float
    '''

    hit_counter = 0
    latitudeMean = 0
    longitudeMean = 0

    for i in range(len(relevant_planes_id)):
        frame = data['data'][relevant_planes_id[i]]

        if frame['latitude'] is not None:
            hit_counter += 1
            latitudeMean += frame["latitude"]
            longitudeMean += frame["longitude"]

            hit_counter_global += 1
            latitudeMean_global += frame["latitude"]
            longitudeMean_global += frame["longitude"]

    return hit_counter, latitudeMean, longitudeMean, hit_counter_global, latitudeMean_global, longitudeMean_global


def get_cartesian_coordinates(lat=0.0, lon=0.0, alt=0.0, meter = True):

    '''
    Converts Geographical coordinates to cartesian coordinates.

    :param lat: Latitude coordinate in degrees
    :param lon: Longitude coordinate in degrees
    :param alt: Altitude in feet
    :param meter: State variable for determining return unit (metres/feet)
    :type lat: Float
    :type lon: Float
    :type alt: Float
    :type meter: Boolean
    :return: Latitude, Longitude, Altitude in metres
    :rtype: Float
    '''

    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    R_earth = 6371000.0 # radius of the earth in meters
    altitude = alt
    if meter == False:
        altitude = altitude * 0.3048 # from feet to meters
    R = R_earth + altitude

    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)

    return x, y, z


def get_geo_coordinates(x, y, z):
    '''
    Converts cartesian coordinates to geographical coordinates.

    :param x: Latitude in metres
    :param y: Longitude in metres
    :param z: Altitude in metres
    :type x: Float
    :type y: Float
    :type z: Float
    :return: Latitude, longitude, altitude in geographic coordinates.
    :rtype: Float
    '''
    R = np.sqrt(x**2 + y**2 + z**2)
    lat = np.arcsin(z / R)
    lon = np.arctan2(y, x)

    return np.rad2deg(lon), np.rad2deg(lat), R


def calculate_position(all_seen_planes, data):
    '''
    This function calculates the position of all the icaos successively, both using the 'Globally unambigous' method and the 'Locally unambigous method'
    Even after several corrective checks on the frames, there is still a possibility for the frames to carry wrong data. Thus, the calculated position is verified by both the steps and an average
    of all the positions is mantained which acts as a reference position.

    :param all_seen_planes: List of unique icao addresses present in the recording
    :param data: JSON containing the entire set of frame data found in the recording
    :type all_seen_planes: Python List
    :type data: Python dictionary
    :return: The updated data dictionary with the locations (only for position frames)
    :rtype: Python dictionary
    '''

    latRef = data["meta"]["gs_lat"]
    lonRef = data["meta"]["gs_lon"]

    latGlobal = latRef
    lonGlobal = lonRef

    hit_counter_global = 0
    latitudeMean_global = 0
    longitudeMean_global = 0

    print("there are", len(all_seen_planes), "planes")

    for plane in all_seen_planes:
        '''
        Position decoding by the globally unambigous position (aka Two frame method)
        '''
        #print(plane)
        relevant_planes_id = []

        for frame in data["data"]:
            if plane == frame["ICAO"] and identifier3(frame["df"], frame["tc"]):
                relevant_planes_id.append(frame["id"])


        # finding just alternating "frames"
        frame_b4 = 0
        id_b4 = 0

        for i in range(len(relevant_planes_id)):
            frame = data["data"][relevant_planes_id[i]]

            if i > 0:
                if frame_b4 != frame["F"]:

                    # do positioning here with one alternating even and odd frame

                    if frame["F"] == 0:
                        # frame is even
                        lat_even = frame["LAT_CPR"]
                        t_even = frame["id"]

                        lon_even = frame["LON_CPR"]

                        lat_odd = data["data"][id_b4]["LAT_CPR"]
                        t_odd = data["data"][id_b4]["id"]

                        lon_odd = data["data"][id_b4]["LON_CPR"]

                    else:
                        # frame is odd
                        lat_even = data["data"][id_b4]["LAT_CPR"]
                        t_even = data["data"][id_b4]["id"]

                        lon_even = data["data"][id_b4]["LON_CPR"]

                        lat_odd = frame["LAT_CPR"]
                        t_odd = frame["id"]

                        lon_odd = frame["LON_CPR"]

                    nl_lat = latitude(lat_even, lat_odd, t_even, t_odd)
                    nl_lon = longitude(lon_even, lon_odd, t_even, t_odd, nl_lat)

                    frame['latitude'] = nl_lat
                    frame['longitude'] = nl_lon


            #data["data"][relevant_planes_id[i]] = frame
            frame_b4 = data["data"][relevant_planes_id[i]]["F"]
            id_b4 = frame["id"]


        # finding the mean location of all planes
        hit_counter, latitudeMean, longitudeMean, hit_counter_global, latitudeMean_global, longitudeMean_global = \
            get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global)


    if hit_counter_global != 0:
        latGlobal = latitudeMean_global / hit_counter_global
        lonGlobal = longitudeMean_global / hit_counter_global


    # todo: adding a logic to decide whether to take the generated latGlobal or lonGlobal or the groundstation setup.


    # still the odd-even method, but checking for outliers and rpearing them.
    for plane in all_seen_planes:
        #print(plane)
        relevant_planes_id = []

        for frame in data["data"]:
            if plane == frame["ICAO"] and identifier3(frame["df"], frame["tc"]):
                #print(frame["ICAO"], frame["id"], frame["F"], frame["ALT"], frame["LAT_CPR"], frame['LON_CPR'])
                relevant_planes_id.append(frame["id"])


        for i in range(len(relevant_planes_id)):
            frame = data['data'][relevant_planes_id[i]]

            if frame['latitude'] is not None or frame['longitude'] is not None and identifier3(frame["df"], frame["tc"]):
                lat_ambigous, lon_ambigous = pos_local(latGlobal, lonGlobal, frame["F"], frame["LAT_CPR"], frame["LON_CPR"])

                if frame['latitude'] != lat_ambigous or frame['longitude'] != lon_ambigous:
                    frame['latitude'] = lat_ambigous
                    frame['longitude'] = lon_ambigous

            #data['data'][relevant_planes_id[i]] = frame
        hit_counter, latitudeMean, longitudeMean, hit_counter_global, latitudeMean_global, longitudeMean_global = \
                 get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global)


    if hit_counter_global != 0:
        latGlobal = latitudeMean_global / hit_counter_global
        lonGlobal = longitudeMean_global / hit_counter_global


    # finding the leftover positions
    hit_counter_global = 0
    latitudeMean_global = 0
    longitudeMean_global = 0

    '''
    Decoding the frames that had escaped the initial decoding run.
    '''
    for plane in all_seen_planes:
        relevant_planes_id = []

        for frame in data["data"]:
            if plane == frame["ICAO"] and identifier3(frame["df"], frame["tc"]):
                relevant_planes_id.append(frame["id"])


        for i in range(len(relevant_planes_id)):
            frame = data['data'][relevant_planes_id[i]]

            if frame['latitude'] == None and frame['longitude'] == None and identifier3(frame["df"], frame["tc"]):
                lat_ambigous, lon_ambigous = pos_local(latGlobal, lonGlobal, frame["F"], frame["LAT_CPR"], frame["LON_CPR"])

                frame['latitude'] = lat_ambigous
                frame['longitude'] = lon_ambigous


        # todo after the odd-even positioning, the average position can be used for latRef and lonRef
        hit_counter, latitudeMean, longitudeMean, hit_counter_global, latitudeMean_global, longitudeMean_global = \
            get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global)


    if hit_counter_global != 0:
        latGlobal = latitudeMean_global / hit_counter_global
        lonGlobal = longitudeMean_global / hit_counter_global

    print("possible groundstation location", latGlobal, lonGlobal)

    return data



def calculate_velocity(data):

    for i in range(len(data['data'])):
        frames = data['data'][i]
        if identifier4(frames['df'], frames['tc']):
            if frames['Subtype'] == 1:
                frames['isGspeed'] = 1
                #Horizontal velocity Calculation Below
                if frames['S_ew'] == 1:
                    Vwe = -1 * (frames['V_ew'] - 1)
                else:
                    Vwe = frames['V_ew'] -1
                if frames['S_ns'] == 1:
                    Vsn = -1 * (frames['V_ns'] - 1)
                else:
                    Vsn = (frames['V_ns'] - 1)

                vel = ((Vwe ** 2) + (Vsn ** 2)) ** 0.5
                hdg = (math.atan2(Vwe, Vsn)*360) / (2 * math.pi)
                if hdg < 0:
                    hdg += 360

                frames['heading'], frames['velocity'] = hdg, vel
                #Vertical Rate calculation Below
                '''
                To be taken care of: VrSrc : Baro-pressure change/geometric change
                '''
                Vr = (frames['Vr'] -1) * 64
                frames["vert_rate"] = Vr if frames['S_vr'] == 0 else Vr*-1

            elif frames['Subtype'] == 3:
                #Airspeed Calculation
                hdg = None
                if frames['S_hdg'] == 1:
                    hdg = frames['Hdg'] / 1024 * 360
                frames['heading'] = hdg
                '''
                To be taken care of: AS_t
                0/1::IAS/TAS
                '''
                #Airspeed calculation below
                frames['isGspeed'] = 0
                frames['velocity'] = frames['AS']

                #Vertical rate Below
                Vr = (frames['Vr'] -1) * 64
                frames["vert_rate"] = Vr if frames['S_vr'] == 0 else Vr*-1


    return data


def convert_position(data):

    for i in range (len(data["data"])):
        frames = data['data'][i]

        if frames["latitude"] is not None and frames["longitude"] is not None and frames["altitude"] is not None:
            frames["x"], frames["y"], frames["z"] = get_cartesian_coordinates(frames["latitude"],
                                                                              frames["longitude"],
                                                                              frames["altitude"],
                                                                              False)


    return data
