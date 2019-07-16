import argparse
import os
from planespotting import utils, calculator
from planespotting.decoder import decode
from planespotting import multilateration
import time


samplerate = 2000000 # of the recorded IQ date with 2MHz for each I and Q
samplerate_avrmlat = 12000000 # AVR, freerunning 48-bit timestamp @ 12MHz


def load_dump1090_file(file):
    '''
    The json from the input file is loaded here.

    A new empty json structure gets initialised here and the raw data from the
    input file is plugged into this new json.

    What is this new json structure: It contains all the keys to all possible data that
                                    can be extracted using the decoder script. The decoder.py files
                                    fills up the keys in them.

    :param file: JSON input file
    :type file: File Object
    :return: JSON
    :rtype: dictionary
    '''

    dump1090_msg = []

    json_data = utils.const_frame()
    json_data["meta"]["file"] = file.split(os.sep)[-1]
    json_data["meta"]["mlat_mode"] = "avrmlat"
    if os.path.exists(file) and utils.is_binary(file) is False:
        with open(file, 'r') as infile:

            id = 0
            payload = []

            for line in infile:
                line = line.rstrip()

                if line.startswith("@") and line.endswith(";"):
                    data = utils.const_frame_data()['data']

                    data['id'] =  id
                    data['raw'] = line
                    data['SamplePos'] = int(line[1:13], 16) // (samplerate_avrmlat // samplerate) - (112 + 8) * 2
                    data['adsb_msg'] = line[13:-1]
                    payload.append(data)

                    id += 1

            json_data["data"] = payload

    return json_data

def get_gs_data(station, path):
    data = utils.load_json(path)

    return data[station]




def main(filename, output, latitude, longitude, altitude):
    '''
    The expected inputs to the filename parameter: Path to a file, path to a folder.

    :param filename: The path to the folder/file which cotains the RAW ADS-B.
    :param output: Output path
    :param latitude: Latitude coordinate of the ground station
    :param longitude: Longitude coordinate of the ground station

    '''


    path = "data" + os.sep + "adsb"

    if output is not None:
        if output.find(os.sep, 0) != len(output) - 1:
            path = output + os.sep + "data" + os.sep + "adsb"
        else:
            path = output + "data" + os.sep + "adsb"


    if os.path.isdir(filename):
        print("loading in all files in folder:", filename)

        processing_files = utils.get_all_files(filename)

    elif os.path.isfile(filename):
        print("loading in this file:", filename)

        processing_files = utils.get_one_file(filename)

    else:
        print("neither file, nor folder. ending programme.")
        return

    if len(processing_files) == 0:
        exit("No input files found in the directory. Quitting")


    print("processing", len(processing_files))
    print("")
    for file in processing_files:
        print("processing", file)
        print(file.split(os.sep)[1])

        data = load_dump1090_file(file)
        gs_data = get_gs_data(file.split(os.sep)[1], "planespotting"+os.sep+"gs_data.json")
        latitude, longitude, altitude = calculator.get_cartesian_coordinates(gs_data['lat'], gs_data['lon'], gs_data['alt'], True)

        # print(latitude, longitude, altitude)
        # exit()

        if data["meta"]["gs_lat"] is None and data["meta"]["gs_lon"] is None and \
                        latitude is not None and longitude is not None:
            # if the gs location is already set, we don't need the inputs.
            # if they are set, we take them from the loaded data structure.
            data["meta"]["gs_lat"] = float(latitude)
            data["meta"]["gs_lon"] = float(longitude)
            data["meta"]["gs_alt"] = float(altitude)
            data["meta"]["rec_start"] = time.time()
            data["meta"]["rec_end"] = time.time() + 120
        print("input lat & long:", data["meta"]["gs_lat"], data["meta"]["gs_lon"])

        data = decode(data)

        print("storing adsb-data")

        if "gzip" == "gzip":
            # standard output
            utils.store_file_jsonGzip(path, file, data)
        else:
            utils.store_file(path, file, data)

    print("doing mlat stuff from here on...")
    multilateration.main(path)


def getArgs():
    '''
    defining the input parameters by the arguments.

    src: https://pymotw.com/2/argparse/

    :return: args
    :rtype: argparse.Namespace
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--from', action='store', default="input"+os.sep,
                        dest='file',
                        help='load in the file or folder')

    parser.add_argument('--lat', action='store', default=None,
                        dest='latitude',
                        help='sets the groundstation latitude')

    parser.add_argument('--lon', action='store', default=None,
                        dest='longitude',
                        help='sets the groundstation longitude')

    parser.add_argument('--alt', action='store', default=0.0,
                        dest='altitude',
                        help='sets the groundstation altitude')

    parser.add_argument('-o', '--output', action='store', default=None,
                        dest='output',
                        help='Path to output file')


    #parser.add_argument('--version', action='version', version='0.0') keeping this comment for future reminder
    return parser.parse_args()


if __name__ == '__main__':
    args = getArgs()

    main(args.file, args.output, args.latitude, args.longitude, args.altitude)
