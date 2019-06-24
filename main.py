import argparse
import os
from planespotting import utils
from planespotting.decoder import decode


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


def main(filename, latitude, longitude):
    '''
    The expected inputs to the filename parameter: Path to a file, path to a folder.
    '''
    if os.path.isdir(args.file):
        print("loading in all files in folder:", filename)

        processing_files = utils.get_all_files(filename)

    elif os.path.isfile(args.file):
        print("loading in this file:", filename)

        processing_files = utils.get_one_file(filename)

    else:
        print("neither file, nor folder. ending programme.")
        return


    print("processing", len(processing_files))
    print("")
    for file in processing_files:
        print("processing", file)

        data = load_dump1090_file(file)

        if data["meta"]["gs_lat"] is None or data["meta"]["gs_lon"] is None:
            # if the gs location is already set, we don't need the inputs.
            # if they are set, we take them from the loaded data strcture.
            data["meta"]["gs_lat"] = latitude
            data["meta"]["gs_lon"] = longitude

        print(data["meta"]["gs_lat"], data["meta"]["gs_lon"])

        data = decode(data)

        print("convert raw adsb files")

        print("decode converted raw adsb files")

        print("decode again planes by icao address. #1")
        print("decode again planes by icao address. #n")
        print("")

        print("storing adsb-data")
        path = "data" + os.sep + "adsb"
        utils.store_file(path, file, data)


def getArgs():
    '''
    defining the input parameters by the arguments.

    src: https://pymotw.com/2/argparse/

    :return: args
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--from', action='store', default=os.sep,
                        dest='file',
                        help='load in the file or folder')

    parser.add_argument('--lat', action='store', default=None,
                        dest='latitude',
                        help='sets the groundstation latitude')

    parser.add_argument('--lon', action='store', default=None,
                        dest='longitude',
                        help='sets the groundstation longitude')

    #parser.add_argument('--version', action='version', version='0.0') keeping this comment for future reminder

    return parser.parse_args()


if __name__ == '__main__':
    args = getArgs()

    main(args.file, args.latitude, args.longitude)
