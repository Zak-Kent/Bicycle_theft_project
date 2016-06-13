import project_config
import psycopg2

try:
    conn = psycopg2.connect(dbname=project_config.dbname, user=project_config.user, 
        host=project_config.host, password=project_config.password)
    print("connected to db")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

def empty_grid_finder(a_square_id):
    """check the 25 surrounding grid spaces in box-like shape including center point, write a 1 to square's 'valid_data' 
    column if there is data for neighbors or self, write a zero if no data"""

    sql_select_grids = """SELECT id, test_geom, num_racks, num_corners, num_thefts FROM theft_grid
        ORDER BY test_geom <-> (SELECT test_geom FROM theft_grid WHERE id = %s)
        LIMIT 25;"""

    sql_select_data = (a_square_id,)
    cur.execute(sql_select_grids, sql_select_data)
    nbor_squares = cur.fetchall()

    sql_write = """UPDATE theft_grid SET valid_data = %s WHERE id = %s"""

    for square in nbor_squares: 
        if square[2] > 0 or square[3] > 0 or square[4] > 0: 
            valid_val = 1 
            break    
        else: 
            valid_val = 0

    sql_write_data = (valid_val, a_square_id)
    cur.execute(sql_write, sql_write_data)

    conn.commit()

# sql_grid_select = """SELECT id FROM theft_grid WHERE valid_data IS NULL AND num_racks IS NOT NULL;"""
# cur.execute(sql_grid_select)

# square_ids = cur.fetchall()

# for square in square_ids:
#     empty_grid_finder(square[0])




