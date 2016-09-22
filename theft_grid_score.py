import bilinearinter
import psycopg2
import project_config

try:
    conn = psycopg2.connect(dbname=project_config.dbname, user=project_config.user, 
        host=project_config.host, password=project_config.password)
    print("connected to db")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

def grid_score_calc(grid_info, occupancy_rate):
    """take info from single grid square and occupancy_rate, calculate and return that grid's center point theft score. 

    grid_info's format: (num_racks, num_corners, num_thefts)
    >>> grid_info = (5, 2, 10)
    >>> grid_score_calc(grid_info, .5)
    0.5795574288724974
    """
    # variable used to assume one theft and one rack at all locations 
    norm = 1 

    # calculate the approx num of bikes in area over 8 years of data 
    bicycles_in_area_8_years = ((grid_info[0] * 2 + (grid_info[1] + norm)) * 365 * 8) * occupancy_rate 

    # multiply the percentage by 1000 to move results up 3 decimal places
    stolen_bicycle_percentage = (grid_info[2] + norm) / bicycles_in_area_8_years * 1000

    return stolen_bicycle_percentage

def grid_scores():
    """calculate indivdual theft score per grid in DB"""

    sql_grid = """SELECT id, num_racks, num_corners, num_thefts FROM theft_grid WHERE grid_score IS NULL;"""
    cur.execute(sql_grid)
    squares = cur.fetchall()

    sql_write = """UPDATE theft_grid SET grid_score = %s WHERE id = %s;"""

    for item in squares: 
        # use helper function grid_score_calc to find grid score 
        grid_args = (item[1], item[2], item[3])
        score = grid_score_calc(grid_args, .3)

        sql_write_data = (score, item[0])
        cur.execute(sql_write, sql_write_data)

    conn.commit()   
#grid_scores()

def zeros(): 
    """select all rows with Null values and change Null value to zero"""
    sql_zeros = """SELECT id, num_thefts FROM theft_grid WHERE num_thefts IS NULL;"""

    cur.execute(sql_zeros)
    nulls = cur.fetchall()

    sql_write = """UPDATE theft_grid SET num_thefts = 0 WHERE id = %s"""

    for item in nulls:
        sql_write_data = (item[0],) 
        cur.execute(sql_write, sql_write_data)

    conn.commit()
#zeros()

def center_point_maker():
    """make center point of grid boxes as a geom point"""

    sql_grid_boxes = """SELECT st_centroid(geom), id FROM theft_grid WHERE point_geom IS NULL;"""

    cur.execute(sql_grid_boxes)
    boxes = cur.fetchall()

    sql_write = """UPDATE theft_grid SET point_geom = %s WHERE id = %s;"""
    
    for item in boxes:
        sql_write_data = (item[0], item[1])
        cur.execute(sql_write, sql_write_data)
    conn.commit()
#center_point_maker()

def point_transform():
    """take a set of points and transform their projections to SRID 4326"""
    sql_select = """SELECT st_transform(point_geom, 4326), id FROM theft_grid WHERE test_geom IS NULL;"""
    cur.execute(sql_select)
    test = cur.fetchall()

    sql_write = """UPDATE theft_grid SET test_geom = %s WHERE id = %s;"""
    
    for item in test: 
        sql_write_data = (item[0], item[1])
        cur.execute(sql_write, sql_write_data)
    conn.commit()
#point_transform()

#print(grid_score_calc([None, 0, 0], .3))

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()