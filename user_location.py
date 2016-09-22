import bilinearinter
import logging
import project_config
import psycopg2
import square_check


class location_info:
    """take users lat/long and create an object that has methods to return their interpolated score and a list of 
        bicycle racks and their scores within a given distance""" 

    def __init__(self, lati, longi):
        self.lati = lati
        self.longi = longi
        self.cursor = self.db_connect()
        self.geom = self.location_geom()

    def __str__(self):
        return "user lat: {}, user long: {}".format(str(self.longi), str(self.lati))

    def db_connect(self):
        try:
            self.conn = psycopg2.connect(dbname=project_config.dbname, user=project_config.user, 
                host=project_config.host, password=project_config.password)
            logging.debug("connected to db")
            self.cur = self.conn.cursor()
            return self.cur

        except:
            logging.debug("I am unable to connect to the database")

    def location_geom(self):
        """use object's lati/longi to create a geometry object in postgis"""

        point = 'POINT({} {})'.format(self.longi, self.lati)
        sql_state = """SELECT ST_GeomFromText(%s, 4326)"""
        sql_data = (point,)
        self.cursor.execute(sql_state, sql_data)

        geom = self.cursor.fetchone()
        logging.debug("point geom: {}".format(geom[0]))
        return geom[0] 

    def racks_within_distance(self, dist=150):
        """find all racks within provied dist value and return their lat/long, and theft_score"""

        sql_state = """SELECT bilinear_score, degy, degx, gid 
        FROM bicycle_parking_pdx
        WHERE ST_Distance(%s::geography, bicycle_parking_pdx.geom::geography) <= %s;"""
        sql_data = (self.geom, dist)
        self.cursor.execute(sql_state, sql_data)

        racks = self.cursor.fetchall()
        logging.debug(racks)

        return racks

    def user_theft_score(self):
        """use interpolation to calculate user's score based on their lat/long"""

        # Need 7 to make sure to include the 4 points that make square around user  
        sql_corners = """SELECT degx, degy, id, grid_score FROM theft_grid
            ORDER BY test_geom <-> %s
            LIMIT 7;"""

        sql_data = (self.geom,)
        self.cursor.execute(sql_corners, sql_data)
        points = self.cursor.fetchall()

        # convert self.longi (user longitude) to positive number so square check/interpolation math works
        pos_longi = self.longi * -1

        sq_point_ids = square_check.square_check(points, pos_longi, self.lati)

        # pull out points that make a square from 7 selected in first sql statement using ids from square_check 
        # make each point in (degx, degy, score) format 
        square_points = [((item[0] * -1), item[1], float(item[3]))for item in points if item[2] in sq_point_ids]
        logging.debug("point ids {}".format(square_points))

        # use bilinearinter file to calculate user's theft score at their location 
        interpolation_val = bilinearinter.bilinear_interpolation(pos_longi, self.lati, square_points)
        logging.debug(interpolation_val)

        return interpolation_val


def test():
    import doctest
    logging.basicConfig(format='%(levelname)s %(funcName)s %(lineno)d:%(message)s', level=logging.DEBUG)
    doctest.testmod()

if __name__ == '__main__':
    test()

    test = location_info(45.519003, -122.683648)
    test.racks_within_distance(30)
    test.user_theft_score()
