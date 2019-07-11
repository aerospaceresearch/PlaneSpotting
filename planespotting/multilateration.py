from planespotting.calculator import *
from planespotting import utils
from pathlib import Path
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

    for file in processing_files:
        print("processing", file)

        if Path(file).suffix == ".gz":
            data = load_file_jsonGzip(file)

        else:
            with open(file, 'r') as f:
                data = json.load(f)

        #print(data)
        conn = sqlite3.connect('planespotting/test.db')
        # records= []
        # for frame in data['data']:
        #     record = (frame['id'], frame['raw'], frame['adsb_msg'], frame['timestamp'], frame['SamplePos'], frame['df'], frame['tc'], frame['x'], frame['y'], frame['z'], frame['time_propagation'], data['meta']['file'], data['meta']['mlat_mode'], data['meta']['gs_lat'], data['meta']['gs_lon'], data['meta']['gs_alt'])
        #     records.append(record)
        # conn.executemany("INSERT INTO frames VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", records)
        # conn.commit()
        data = conn.execute("SELECT * FROM frames WHERE df = 17 AND tc BETWEEN 9  AND 18")
        for rows in data:
            print(rows)

        conn.close()
