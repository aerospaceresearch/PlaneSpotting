from planespotting.identifiers import *
from planespotting.utils import *

#All imports end here
latRef = 50.9
lonRef = 11.6

def calculator(all_seen_planes, data):

    print(len(all_seen_planes))

    for plane in all_seen_planes:
        print(plane)
        relevant_planes_id = []

        for frame in data["data"]:
            if plane == frame["ICAO"] and identifier3(frame["df"], frame["tc"]):
                #print(frame["ICAO"], frame["id"], frame["F"], frame["ALT"], frame["LAT_CPR"], frame['LON_CPR'])
                relevant_planes_id.append(frame["id"])


        # finding just alternating "frames"
        frame_b4 = 0
        id_b4 = 0

        for i in range(len(relevant_planes_id)):
            frame = data["data"][relevant_planes_id[i]]
            frame['altitude'] = altitude(frame['ALT'])

            if i > 0:
                if frame_b4 != frame["F"]:
                    #print(frame["ICAO"], frame["id"], frame["F"], frame["T"], frame["ALT"], frame["LAT_CPR"], frame['LON_CPR'])

                    # do positioning here with one alternating even and odd frame
                    # print(id_b4, frame["id"])

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


                    lat_ambigous, lon_ambigous = pos_local(latRef, lonRef, frame["F"], frame["LAT_CPR"], frame["LON_CPR"])
                    if nl_lat != lat_ambigous or nl_lon != lon_ambigous:
                        #print(">>>", stray position detected)
                        nl_lat = lat_ambigous
                        nl_lon = lon_ambigous

                    frame['latitude'] = nl_lat
                    frame['longitude'] = nl_lon


            data["data"][relevant_planes_id[i]] = frame
            frame_b4 = data["data"][relevant_planes_id[i]]["F"]
            id_b4 = frame["id"]


        #todo after the odd-even positioning, the average position can be used for latRef and lonRef


        # finding the leftover positions

        for i in range(len(relevant_planes_id)):
            frame = data['data'][relevant_planes_id[i]]

            if frame['latitude'] == None and frame['longitude'] == None and identifier3(frame["df"], frame["tc"]):
                lat_ambigous, lon_ambigous = pos_local(latRef, lonRef, frame["F"], frame["LAT_CPR"], frame["LON_CPR"])

                frame['latitude'] = lat_ambigous
                frame['longitude'] = lon_ambigous