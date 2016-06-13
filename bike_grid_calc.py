import project_config
import psycopg2

try:
    conn = psycopg2.connect(dbname=project_config.dbname, user=project_config.user, 
        host=project_config.host, password=project_config.password)
    print("connected to db")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

# this query takes way too long to run, maybe try creating a point layer using st_centroid for each polygon 
def street_corners_per_grid():
    """find the number of street corners inside each grid and write that number to each grid's num_corners column"""

    sql_corners = """SELECT theft_grid.id, count(*) AS total FROM theft_grid, corner_improved_pdx 
        WHERE st_intersects(theft_grid.geom, st_makevalid(corner_improved_pdx.geom)) GROUP BY theft_grid.id;"""

    cur.execute(sql_corners)
    corner_list = cur.fetchall()

    sql_write = "UPDATE theft_grid SET num_corners = %s WHERE id = %s;"

    for item in corner_list:
        sql_write_data = (item[1], item[0])
        cur.execute(sql_write, sql_write_data)

    conn.commit()
#street_corners_per_grid()

def make_centroid_points():
    """convert polygon corner data into point data and write to seperate table"""

    sql_corners = """SELECT gid FROM corner_improved_pdx;"""
    cur.execute(sql_corners)
    corner_list = cur.fetchall()

    sql_corner_convert = """SELECT st_centroid(st_makevalid(geom)) FROM corner_improved_pdx WHERE gid = %s;"""

    exceptions = 0 
    for item in corner_list:
        try: 
            sql_data = (item[0],)
            cur.execute(sql_corner_convert, sql_data)
            geom_point = cur.fetchone()
        except:
            print("exception")
            exceptions += 1
            continue 

        sql_write = """INSERT INTO corner_points (id, geom) VALUES (%s, %s)"""
        sql_write_data = (item[0], geom_point[0])
        cur.execute(sql_write, sql_write_data)
        conn.commit()

    print("exceptions = {}".format(exceptions))
#make_centroid_points()

def parking_spaces_per_grid():
    """find the number of bicycle racks inside each grid and write that number to each grid's num_racks column"""

    sql_racks = """SELECT theft_grid.id, count(*) AS total FROM theft_grid, bicycle_parking_pdx 
        WHERE st_intersects(theft_grid.geom, st_transform(bicycle_parking_pdx.geom, 2913)) GROUP BY theft_grid.id;"""

    cur.execute(sql_racks)
    grid_list = cur.fetchall()

    sql_write = """UPDATE theft_grid SET num_racks = %s WHERE id = %s;"""

    for item in grid_list:
        sql_write_data = (item[1], item[0])
        cur.execute(sql_write, sql_write_data)

    conn.commit()
#parking_spaces_per_grid()

def corners_per_grid():
    """find the number of corners inside each grid and write that number to each grid's num_corners column"""

    sql_corners = """SELECT theft_grid.id, count(*) AS total FROM theft_grid, corner_points 
        WHERE st_intersects(theft_grid.geom, corner_points.geom) GROUP BY theft_grid.id;"""

    cur.execute(sql_corners)
    grid_list = cur.fetchall()

    sql_write = """UPDATE theft_grid SET num_corners = %s WHERE id = %s;"""

    for item in grid_list:
        sql_write_data = (item[1], item[0])
        cur.execute(sql_write, sql_write_data)

    conn.commit()
#corners_per_grid()

def thefts_per_grid():
    """find the number of thefts inside each grid and write that number to each grid's num_thefts column"""

    sql_thefts = """SELECT theft_grid.id, count(*) AS total FROM theft_grid, bicycle_thefts_pdx 
        WHERE st_intersects(theft_grid.geom, st_transform(bicycle_thefts_pdx.geom, 2913)) GROUP BY theft_grid.id;"""

    cur.execute(sql_thefts)
    grid_list = cur.fetchall()

    sql_write = """UPDATE theft_grid SET num_thefts = %s WHERE id = %s;"""

    for item in grid_list:
        sql_write_data = (item[1], item[0])
        cur.execute(sql_write, sql_write_data)

    conn.commit()
#thefts_per_grid()



