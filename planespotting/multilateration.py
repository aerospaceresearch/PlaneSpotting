from planespotting.calculator import *
from planespotting import utils


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

    # sorting the files for overlapping time spans
    for file_base in processing_files:
        print("processing", file_base)

        data_base = load_file_json(file_base)

        start_base = float(data_base["meta"]["gs_rec_timestamp_start"])

        if data_base["meta"]["gs_rec_timestamp_end"] is not None:
            end_base = float(data_base["meta"]["gs_rec_timestamp_end"])

        else:
            end_base = float(data_base["meta"]["gs_rec_timestamp_start"]) + \
                  float(data_base["data"][-1]["SamplePos"]) / float(data_base["meta"]["gs_rec_samplingrate"])


        # in this, we will store the overlapping files we will later process further
        load_files = []

        for file_compare in processing_files:

            data_compare = load_file_json(file_compare)

            start_compare = float(data_compare["meta"]["gs_rec_timestamp_start"])

            if data_compare["meta"]["gs_rec_timestamp_end"] is not None:
                end_compare = float(data_compare["meta"]["gs_rec_timestamp_end"])

            else:
                end_compare = float(data_compare["meta"]["gs_rec_timestamp_start"]) + \
                              float(data_compare["data"][-1]["SamplePos"]) / float(data_compare["meta"]["gs_rec_samplingrate"])



            if start_compare <= start_base <= end_compare and start_compare <= end_base <= end_compare:
                print("file is fully inside basefile")

            if start_compare <= start_base <= end_compare is True and \
                                            start_compare <= end_base <= end_compare is False:
                print("file is starting in basefile and ends later")

            if start_compare <= start_base <= end_compare is False and \
                                            start_compare <= end_base <= end_compare is True:
                print("file is ending in basefile and starts earlier")

            if start_compare <= start_base <= end_compare is False and \
                                            start_compare <= end_base <= end_compare is False:
                print("file is not overlapping with basefile")


            if start_compare <= start_base <= end_compare or start_compare <= end_base <= end_compare:
                #storing all overlapping files
                load_files.append(file_compare)


        print("these", len(load_files), "files overlap:", load_files)