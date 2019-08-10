from planespotting.calculator import *
from planespotting import utils
from pathlib import Path
import os
import sqlite3

def create_table():
    '''
    This function is used to create a sqlite database which is used for searching for unique frames present in different files, or station recordings.

    :param: None
    :return: Void
    '''
    conn = sqlite3.connect('planespotting/data.db')

    conn.execute('''CREATE TABLE frames
             (id INT PRIMARY KEY,
             raw TEXT,
             adsb_msg TEXT,
             timestamp TEXT,
             SamplePos TEXT,
             df INT,
             tc INT,
             x TEXT,
             y TEXT,
             z TEXT,
             time_propagation TEXT,
             file TEXT,
             mlat_mode TEXT,
             gs_id TEXT,
             gs_lat FLOAT,
             gs_lon FLOAT,
             gs_alt FLOAT);''')

    conn.close()


def calculate_signalpropagationtime(data):
    '''
    Calculates the time taken for a signal to travel from the aircraft location to the ground station.

    :param data: JSON containing all the frames with decoded data.
    :type data: Python dictionary
    :return: JSON which now contains the time of propagation from aircraft to ground station.
    :rtype: Python dictionary
    '''
    c = 300000000.0 # speed of light

    if data["meta"]["gs_lat"] is not None and data["meta"]["gs_lon"] is not None and data["meta"]["gs_alt"] is not None:
        gs_x, gs_y, gs_z = get_cartesian_coordinates(data["meta"]["gs_lat"], data["meta"]["gs_lon"], data["meta"]["gs_alt"], True)

        for i in range (len(data["data"])):
            frames = data['data'][i]

            if frames["x"] is not None:
                frames["time_propagation"] = ((gs_x - frames["x"])**2 +
                                              (gs_y - frames["y"])**2 +
                                              (gs_z - frames["z"])**2)**0.5 / c

            data['data'][i] = frames

    return data

def correct_samplePos(data):

    samplerate = 2000000 #Hz

    for i in range (len(data["data"])):
        frames = data['data'][i]

        frames["SamplePos"] = frames["SamplePos"] - (frames["time_propagation"] * samplerate)

    return data



def get_files(path):
    '''
    This function is used to get all the files present in a station directory

    :param path: Path to the station directory/folder
    :type path: String
    :return: List of file(s) present inside the given directory
    :rtype: Python List
    '''
    for _, _, files in os.walk(path):
        file = files
    return file

def check_file_overlap(file1, file2):
    '''
    Checks if two files overlap at any point. Both the files are recordings belonging to different ground stations

    :param file1: Path to a recorded file in JSON.
    :param file2: Path to a recorded file in JSON from a different ground station
    :type file1: Python dictionary
    :type file2: Python dictionary
    :return: True/False, whether the two files have an overlap
    :rtype: Boolean
    '''

    data1 = load_file_jsonGzip(file1)
    data2 = load_file_jsonGzip(file2)
    data1_rec_start = data1['meta']['rec_start']

    if data1['meta']['rec_end'] is not None:
        data1_rec_end = float(data1['meta']['rec_end'])
    else:
        data2_rec_end = float(data1['meta']['rec_start']) + float(data1['data'][-1]['SamplePos']) / float(data1['meta']['gs_sampling_rate'])

    data2_rec_start = data2['meta']['rec_start']

    if data2['meta']['rec_end'] is not None:
        data2_rec_end = float(data2['meta']['rec_end'])
    else:
        data2_rec_end = float(data1['meta']['rec_start']) + float(data1['data'][-1]['SamplePos']) / float(data1['meta']['gs_sampling_rate'])

    print("File1_start=", data1_rec_start, "\n", "File1_end", data1_rec_end, "\n", "File2_start", data2_rec_start, "\n", "File2_end", data2_rec_end)

    if (data2_rec_start >= data1_rec_start and data2_rec_end >= data1_rec_end and data1_rec_end > data2_rec_start) or (data2_rec_start <= data1_rec_start and data2_rec_end <= data1_rec_end and data2_rec_end > data1_rec_start):
        return True

    elif (data2_rec_start == data1_rec_start and data2_rec_end == data1_rec_end):
        return True

    elif (data2_rec_start >= data1_rec_start and data2_rec_end <= data1_rec_end):
        return True

    elif (data1_rec_start >= data2_rec_start and data1_rec_end <= data2_rec_end and data1_rec_start < data2_rec_end and data1_rec_end > data2_rec_start):
        return True

    else:
        print("NOT OVERLAPPING")
        return False


def main(path):

    list = []
    stations = os.listdir(path)
    batch = -1
    for i in range(len(stations)):
        mother_file = get_files(path+os.sep+stations[i]+os.sep)

        for m_file in mother_file:
            batch += 1
            list.append([])
            list[batch].append(path+os.sep+stations[i]+os.sep+m_file)

            for j in range(i+1, len(stations)):

                files = get_files(path+os.sep+stations[j]+os.sep)
                for file in files:
                    if check_file_overlap(path+os.sep+stations[i]+os.sep+m_file, path+os.sep+stations[j]+os.sep+file):
                        print(path+os.sep+stations[i]+os.sep+m_file, path+os.sep+stations[j]+os.sep+file)
                        #exit()
                        list[batch].append(path+os.sep+stations[j]+os.sep+file)

            print()
        break
    print(list)
    #exit()
    print("processing mlat")
    print("")

    for processing_files in list:
        print()

        create_table()
        conn = sqlite3.connect('planespotting/data.db')

        for file in processing_files:
            print("processing", file)

            if Path(file).suffix == ".gz":
                data = load_file_jsonGzip(file) #ungzipping

            else:
                with open(file, 'r') as f:
                    data = json.load(f)


            for frame in data['data']:

                if frame['is_repeated'] != int(1):  #skipping the repeated frames in the same file, no idea why they even exist
                    gs_x, gs_y, gs_z = get_cartesian_coordinates(data["meta"]["gs_lat"], data["meta"]["gs_lon"], data["meta"]["gs_alt"], True)
                    record = (i, frame['raw'], frame['adsb_msg'], frame['timestamp'], frame['SamplePos'], frame['df'], frame['tc'], frame['x'], frame['y'], frame['z'], frame['time_propagation'], data['meta']['file'], data['meta']['mlat_mode'], data['meta']['file'], data["meta"]["gs_lat"], data["meta"]["gs_lon"], data["meta"]["gs_alt"])#gs_x, gs_y, gs_z)
                    conn.execute("INSERT INTO frames VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", record)
                    i += 1

                else:
                    continue

        conn.commit()

        cur = conn.cursor()
        cur.execute("SELECT * FROM frames WHERE df = 17 AND tc BETWEEN 9 AND 18") #filtering the position report messages
        data = cur.fetchall()
        uniq_frames = [] #This list will contain df17 and tc9-18 msgs, and each msgs will occur only once in this list, to be used for querying


        for rows in data:
            if rows[2] not in uniq_frames:
                uniq_frames.append(rows[2])

        for frames in uniq_frames: #Looking for the same message in different station file
            cur.execute("SELECT * FROM frames WHERE adsb_msg = ?", (frames,))
            finding = cur.fetchall()
            if len(finding) > 1:
                print(len(finding), finding)
                print("")

        conn.close()
        os.remove("planespotting/data.db") #Throwing away the db
