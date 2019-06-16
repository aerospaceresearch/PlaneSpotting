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