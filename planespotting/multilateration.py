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
    for _, _, files in os.walk(path):
        file = files
    return file #This function is used to get all the files present in a station directory

def main(path):



    chunk_files = []
    gs_no = 0
    print(os.listdir(path))

    reader = []
    list = []

    chunk = 120
    for stations in os.listdir(path):
        chunk_read = 0
        batch = 0

        files = get_files(path+os.sep+stations+os.sep)


        for file in files:
            data = load_file_jsonGzip(path+os.sep+stations+os.sep+file)
            chunk_size = int(data['meta']['rec_end']-data['meta']['rec_start'])
            chunk_read += chunk_size



            if chunk_read > chunk:
                chunk_read = chunk - chunk_size
                batch += 1

            if chunk_read <= chunk: #Creates a nested list for clumped files recorded at the same time at different stations
                try:
                    reader[batch].append(path+os.sep+stations+os.sep+file)

                except:
                    reader.append([])
                    reader[batch].append(path+os.sep+stations+os.sep+file)


    # if os.path.isdir(path):
    #     print("loading in all files in folder:", path)
    #
    #     #processing_files = utils.get_all_files(path)
    #
    # elif os.path.isfile(path):
    #     print("loading in this file:", path)
    #
    #     #processing_files = utils.get_one_file(path)
    #
    # else:
    #     print("neither file, nor folder. ending programme.")
    #     return
    #
    # if len(processing_files) == 0:
    #     exit("No input files found in the directory. Quitting")


    print("processing mlat")
    print("")

    i = 0


    # files = []
    # load_file = []
    # chunk_read = 0
    for processing_files in reader:
        print()

        create_table.create()
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
                    record = (i, frame['raw'], frame['adsb_msg'], frame['timestamp'], frame['SamplePos'], frame['df'], frame['tc'], frame['x'], frame['y'], frame['z'], frame['time_propagation'], data['meta']['file'], data['meta']['mlat_mode'], data['meta']['file'], data['meta']['gs_lat'], data['meta']['gs_lon'], data['meta']['gs_alt'])
                    conn.execute("INSERT INTO frames VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", record)
                    i += 1
                else:
                    continue
        conn.commit()

        cur = conn.cursor()
        cur.execute("SELECT * FROM frames WHERE df = 17 AND tc BETWEEN 9 AND 18") #filtering the position report messages
        data = cur.fetchall()
        uniq_frames = [] #This list will contain df17 and tc9-18 msgs, and each msgs will occur only once in this list, to be used for querying
            #print(data)

        for rows in data:
            if rows[2] not in uniq_frames:
                uniq_frames.append(rows[2])

        for frames in uniq_frames: #Looking for the same message in different station file
            cur.execute("SELECT * FROM frames WHERE adsb_msg = ?", (frames,))
            finding = cur.fetchall()
                # if len(finding) != 5:
            #if len(finding) != 10:
            print(finding)
            print("")

        conn.close()
        os.remove("planespotting/data.db") #Throwing away the db
