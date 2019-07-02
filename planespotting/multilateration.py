from planespotting.calculator import *

def calculate_signalpropagationtime(data):
    c = 300000000.0 # speed of light

    if data["meta"]["gs_lat"] is not None and data["meta"]["gs_lon"] is not None and data["meta"]["gs_alt"] is not None:
        gs_x, gs_y, gs_z = get_cartesian_coordinates(data["meta"]["gs_lat"],
                                                     data["meta"]["gs_lon"],
                                                     data["meta"]["gs_alt"],
                                                     True)

        for i in range (len(data["data"])):
            frames = data['data'][i]

            if frames["x"] is not None and frames["x"] is not None and frames["x"] is not None:
                frames["time_propagation"] = ((gs_x - frames["x"])**2 +
                                              (gs_y - frames["y"])**2 +
                                              (gs_z - frames["z"])**2)**0.5 / c
                print(frames["id"], frames["time_propagation"])

            data['data'][i] = frames

    return data
