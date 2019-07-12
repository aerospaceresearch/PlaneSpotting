from planespotting.calculator import *
from planespotting import utils
from planespotting import create_table
from pathlib import Path
import os
from datetime import datetime, timedelta
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

    samplerate = 2000000 #MHz

    for i in range (len(data["data"])):
        frames = data['data'][i]

        frames["SamplePos"] = frames["SamplePos"] - (frames["time_propagation"] * samplerate)

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

    i = 0
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

        exit(datetime.striptime(data['meta']['rec_start'])-datetime.striptime(data['meta']['rec_end']))

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
