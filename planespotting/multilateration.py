from planespotting.calculator import *
from planespotting import utils
from pathlib import Path


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

            data['data'][i] = frames

    return data


def main(path):

    if os.path.isdir(path):
        print("loading in all files in folder:", path)

        processing_files = utils.get_all_files(path)

    elif os.path.isfile(path):
        print("loading in this file:", path)

        processing_files = utils.get_one_file(path)

    else:
        print("neither file, nor folder. ending programme.")
        return

    if len(processing_files) == 0:
        exit("No input files found in the directory. Quitting")


    print("processing mlat")
    print("")

    for file in processing_files:
        print("processing", file)

        if Path(file).suffix == ".gz":
            data = load_file_jsonGzip(file)

        else:
            with open(file, 'r') as f:
                data = json.load(f)

        print(data["meta"])