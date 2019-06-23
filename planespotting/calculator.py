from planespotting.identifiers import *
from planespotting.utils import *

#All imports end here


def get_meanposition(data, relevant_planes_id, hit_counter_global, latitudeMean_global, longitudeMean_global):
    hit_counter = 0
    latitudeMean = 0
    longitudeMean = 0

    for i in range(len(relevant_planes_id)):
        frame = data['data'][relevant_planes_id[i]]

        if frame['latitude'] is not None:
            # print(frame["ICAO"], frame["latitude"], frame["longitude"])
            hit_counter += 1
            latitudeMean += frame["latitude"]
            longitudeMean += frame["longitude"]

            hit_counter_global += 1
            latitudeMean_global += frame["latitude"]
            longitudeMean_global += frame["longitude"]

    return hit_counter, latitudeMean, longitudeMean, hit_counter_global, latitudeMean_global, longitudeMean_global


def calculate_pos(all_seen_planes, data):

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
                #print(frame["ICAO"], frame["id"], frame["F"], frame["ALT"], frame["LAT_CPR"], frame['LON_CPR'])
                relevant_planes_id.append(frame["id"])


        # finding just alternating "frames"
        frame_b4 = 0
        id_b4 = 0

        for i in range(len(relevant_planes_id)):
            frame = data["data"][relevant_planes_id[i]]

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
                    # print(">>>", stray position detected)
                    frame['latitude'] = lat_ambigous
                    frame['longitude'] = lon_ambigous

            data['data'][relevant_planes_id[i]] = frame




    # finding the leftover positions
    hit_counter_global = 0
    latitudeMean_global = 0
    longitudeMean_global = 0

    for plane in all_seen_planes:
        #print(plane)
        relevant_planes_id = []

        for frame in data["data"]:
            if plane == frame["ICAO"] and identifier3(frame["df"], frame["tc"]):
                #print(frame["ICAO"], frame["id"], frame["F"], frame["ALT"], frame["LAT_CPR"], frame['LON_CPR'])
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



def calculate_vel(data):

    for i in range(len(data['data'])):
        frames = data['data'][i]
        if identifier4(frames['df'], frames['tc']):
            #print(frames['Subtype'])
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
                # data['data'][i] = frames
                # print(data['data'][i])

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
