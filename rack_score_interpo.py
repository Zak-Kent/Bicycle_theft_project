import bilinearinter
import project_config
import psycopg2
import square_check

try:
    conn = psycopg2.connect(dbname=project_config.dbname, user=project_config.user, 
        host=project_config.host, password=project_config.password)
    print("connected to db")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

# need rack id, lat, long 
def rack_score_calc(a_rack):
    """take a geom tag and x, y location of a rack get score at location using bilinear interpolation script
        and write score to rack's bilinear_score column"""

    sql_select_corners = """SELECT degx, degy, id, grid_score FROM theft_grid
            ORDER BY test_geom <-> (SELECT geom FROM bicycle_parking_pdx WHERE gid = %s)
            LIMIT 7;"""

    sql_select_data = (a_rack[0],)
    cur.execute(sql_select_corners, sql_select_data)
    points = cur.fetchall()

    # get id of four points that form a square using square_check.py
    ids = square_check.square_check(points, a_rack[1], a_rack[2])

    # pull out points that make a square from 7 selected in first sql statement using ids from square_check 
    square_points = [((item[0] * -1), item[1], float(item[3]))for item in points if item[2] in ids]

    #####################################################################################################

    # avg = 0 
    # for item in square_points:
    #     avg += item[2]
    # print("avg of all 4 corners {}".format(avg / 4))

    try: 
        interpolation_val = bilinearinter.bilinear_interpolation(a_rack[1], a_rack[2], square_points)
        # print("value from interpolation {}".format(interpolation_val))

        # #checking closest two corners to compare values 
        # sql_corners = """SELECT degx, degy, grid_score FROM theft_grid
        #         ORDER BY test_geom <-> (SELECT geom FROM bicycle_parking_pdx WHERE gid = %s)
        #         LIMIT 2;"""
        # cur.execute(sql_corners, sql_select_data)
        # closest = cur.fetchall()
        # print("closest point value {}, 2nd closest {}".format(closest[0][2], closest[1][2]))
        # print("*" * 60)

    except:
        print("value error on point gid: {}".format(a_rack[0]))
        print("!" * 60)

    
    sql_write = """UPDATE bicycle_parking_pdx SET bilinear_score = %s WHERE gid = %s;"""
    sql_write_data = (interpolation_val, a_rack[0])
    cur.execute(sql_write, sql_write_data)
    conn.commit()

    
    ######################################################################################################



# select racks that don't already have a bilinear score entered 
sql_rack_select = """SELECT gid, degx, degy FROM bicycle_parking_pdx WHERE bilinear_score IS NULL;"""
cur.execute(sql_rack_select)
racks = cur.fetchall()

for item in racks: 
    # change input point values so they match what's needed for interpolation function 
    xcoord = (item[1] * -1)
    value_tup = (item[0], xcoord, item[2])
    rack_score_calc(value_tup)





