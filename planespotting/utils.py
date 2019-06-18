import os

def get_all_files(filename):

    processing_files = []
    for root, dirs, files in os.walk(filename):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.isfile(filepath):
                #print("file", filepath)
                processing_files.append(filepath)

    return processing_files


def get_one_file(filename):
    return [filename]


def is_binary(file):
    try:
        with open(file, 'tr') as check_file:  # try opening file in text mode
            check_file.read()
            return False

    except:  # if false then file is non-binary
        return True


def hexToDec(hexdec):
    dec = int(hexdec, 16)
    return bin(dec)[2:].zfill(56)


def hexToBin(hexdec):
    dec = int(hexdec, 16)
    return bin(dec)[2:].zfill(56)