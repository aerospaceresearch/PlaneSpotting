
import sqlite3
def create():
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
             gs_lat TEXT,
             gs_lon TEXT,
             gs_alt TEXT);''')

    #conn.execute('''CREATE UNIQUE INDEX check ON frames (adsb_msg, gs_id);''')
    conn.close()
