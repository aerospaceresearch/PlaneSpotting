from planespotting.calculator import *
from planespotting import utils
from planespotting import create_table
from pathlib import Path
import os
import sqlite3

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

def correct_samplePos(data):

    samplerate = 2000000 #Hz

    for i in range (len(data["data"])):
        frames = data['data'][i]

        frames["SamplePos"] = frames["SamplePos"] - (frames["time_propagation"] * samplerate)

    return data

def load_station_wise(gs_id, path):

    path = path + os.sep+"station_"+str(gs_id)+os.sep #looking for all recorded files in respective station folder

    return utils.get_all_files(path)

def main(path):

    for i in range(1, 6):
        print(load_station_wise(i, path))
    exit()

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

    i = 0


    files = []
    load_file = []
    chunk_read = 0
    for file in processing_files:

        chunk_length = 240 #seconds
        gs = 5
        file_prefix = "data/adsb/test11"
        data = load_file_jsonGzip(file)
        chunk_read += int(data['meta']['rec_end']-data['meta']['rec_start'])

        if chunk_read >= chunk_length:
            load_file.append(file)
            files.append(load_file)
            load_file = []
            chunk_read = 0
        else:
            load_file.append(file)
            print(load_file)
            print()

    if len(load_file) != 0:
        files.append(load_file)
    exit(files)

    exit()

    create_table.create()
    conn = sqlite3.connect('planespotting/test2.db')

    for file in processing_files:
        print("processing", file)

        if Path(file).suffix == ".gz":
            data = load_file_jsonGzip(file)

        else:
            with open(file, 'r') as f:
                data = json.load(f)

        #print(data)

        #exit(data['meta']['rec_end']-data['meta']['rec_start']) this is time difference

        for frame in data['data']:
            record = (i, frame['raw'], frame['adsb_msg'], frame['timestamp'], frame['SamplePos'], frame['df'], frame['tc'], frame['x'], frame['y'], frame['z'], frame['time_propagation'], data['meta']['file'], data['meta']['mlat_mode'], data['meta']['file'], data['meta']['gs_lat'], data['meta']['gs_lon'], data['meta']['gs_alt'])
            conn.execute("INSERT INTO frames VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", record)
            i += 1
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT * FROM frames WHERE df = 17 AND tc BETWEEN 9 AND 18")
    data = cur.fetchall()
    uniq_frames = [] #This list will contain df17 and tc9-18 msgs, and each msgs will occur only once in this list, to be used for querying
    #print(data)

    for rows in data:
        if rows[2] not in uniq_frames:
            uniq_frames.append(rows[2])

    for frames in uniq_frames:
        cur.execute("SELECT * FROM frames WHERE adsb_msg = ?", (frames,))
        finding = cur.fetchall()
        # if len(finding) != 5:
        print(finding)
        print("")

    conn.close()
    os.remove("planespotting/test2.db") #Throwing away the db
