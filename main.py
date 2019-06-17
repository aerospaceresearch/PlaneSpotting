import argparse
import os

from planespotting import utils


samplerate = 2000000 # of the recorded IQ date with 2MHz for each I and Q
samplerate_avrmlat = 12000000 # AVR, freerunning 48-bit timestamp @ 12MHz


def load_dump1090_file(file):

    dump1090_msg = []

    json_data = {
        "meta" : {
            "file" : file.split(os.sep)[-1],
            "mlat_mode" : ""
        },
        "data" : []
    }

    if os.path.exists(file) and utils.is_binary(file) is False:
        with open(file, 'r') as infile:

            id = 0
            payload = []

            for line in infile:
                line = line.rstrip()
                if line.startswith("@") and line.endswith(";"):
                    data = {
                        "id" : id,
                        "raw" : line,
                        "timestamp" : int(line[1:13], 16) // (samplerate_avrmlat // samplerate) - (112 + 8) * 2,
                        "adsb_msg" : line[13:-1]
                    }

                    payload.append(data)

                id += 1

            json_data["meta"]["mlat_mode"] = "avrmlat"
            json_data["data"] = payload

    return json_data


def main(filename):

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
        load_dump1090_file(file)

        print("convert raw adsb files")

        print("decode converted raw adsb files")

        print("decode again planes by icao address. #1")
        print("decode again planes by icao address. #n")
        print("")


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

    #parser.add_argument('--version', action='version', version='0.0')

    return parser.parse_args()


if __name__ == '__main__':
    args = getArgs()

    main(args.file)