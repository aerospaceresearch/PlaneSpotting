from planespotting.identifiers import *
from planespotting.utils import *
import math
import numpy as np

#All imports end here

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
        return 0
    if(t_even >= t_odd):
        return latEven

    else:
        return latOdd

def longitude(long_cpr_even, long_cpr_odd, t_even, t_odd, nl_lat):  #Calculation of longitude coordinate of the aircraft

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

def get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global):
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


def get_cartesian_coordinates(lat=0.0, lon=0.0, alt=0.0):
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    R_earth = 6371000.0 # radius of the earth in meters
    altitude = alt * 0.3048 # from feet to meters
    R = R_earth + altitude

    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)

    return x, y, z


def get_geo_coordinates(x, y, z):
    R = np.sqrt(x**2 + y**2 + z**2)
    lat = np.arcsin(z / R)
    lon = np.arctan2(y, x)

    return np.rad2deg(lon), np.rad2deg(lat), R


def calculate_position(all_seen_planes, data):

    latRef = data["meta"]["gs_lat"]
    lonRef = data["meta"]["gs_lon"]

    latGlobal = latRef
    lonGlobal = lonRef

    hit_counter_global = 0
    latitudeMean_global = 0
    longitudeMean_global = 0

    print(len(all_seen_planes))

    for plane in all_seen_planes:
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


            data["data"][relevant_planes_id[i]] = frame
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

            data['data'][relevant_planes_id[i]] = frame
        hit_counter, latitudeMean, longitudeMean, hit_counter_global, latitudeMean_global, longitudeMean_global = \
                 get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global)


    if hit_counter_global != 0:
        latGlobal = latitudeMean_global / hit_counter_global
        lonGlobal = longitudeMean_global / hit_counter_global


    # finding the leftover positions
    hit_counter_global = 0
    latitudeMean_global = 0
    longitudeMean_global = 0

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
            data['data'][relevant_planes_id[i]] = frame



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

            data['data'][i] = frames

    return data


def convert_position(data):

    for i in range (len(data["data"])):
        frames = data['data'][i]

        if frames["latitude"] is not None and frames["longitude"] is not None and frames["altitude"] is not None:
            frames["x"], frames["y"], frames["z"] = get_cartesian_coordinates(frames["latitude"], frames["longitude"], frames["altitude"])

        data['data'][i] = frames

    return data
