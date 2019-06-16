import argparse
import os

from planespotting import utils


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
    for file in processing_files:
        print("processing", file)

        print("convert raw adsb files")

        print("decode converted raw adsb files")

        print("decode again planes by icao address. #1")
        print("decode again planes by icao address. #n")


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