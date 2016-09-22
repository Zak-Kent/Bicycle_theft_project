<h1>Bicycle Theft Project</h1>

The goal of this project was to create a database that would help cyclist make informed decisions on the safest places to park their bicycles in the city. 

This repo is a collection of scripts that were used to clean data and build a spatially aware database that helps calculate the rate of theft at city owned bicycle racks in Portland. This database includes open source bicycle theft data from the City of Portland and .shp file data from Portland Atlas. The scripts are a combination of SQL using PostGIS functionality, and Python. Below is a brief description of the project.

During the setup of this database a 2D fishnet of 200m x 200m squares were created across the city of Portland and stored as polygons in the PostgreSQL DB. Also in the database was a collection of points that represented all of the street corners, bicycle racks, and location of bicycle thefts in the city. 

The project calculates the number of bicycle parking opportunities in each square and then estimates the amount of bicycles in that area over the eight years for which we have data. This is done to help deal with potential bias in the theft data. Where there are more bicycles parked on average there may be more thefts but not necessarily a higher rate of theft than another area that has less bicycle traffic. 

To get the rate of theft in each square we take the number of bicycle thefts in that square and divide by the estimate number of bicycles in that area over the eight year period. 

Below is how the rate of theft was calculated. 

Rate of theft = # of thefts + 1 / ((# bicycle parking opportunities + 1) * 365 * 8) * .3 

In the equation above the 1 added to the # of thefts and to the # of parking opportunities is our normalization term and the .3 multiplied at the end represents the average occupancy of bicycle racks which was calculated from a brief survey of racks in Portland. The # of bicycle parking opportunities was calculated by counting the # of street corners and # bicycle racks in each square. Street corners count as one bicycle space and racks as two. 

With the number calculated above we now know the rate of theft at the center point of each square. Because we calculate this rate across the 2D fishnet of squares covering the city we now have a point field of known rates of theft. 

Using the grid of points that represents the known theft rates we can interpolate the rate of theft at any location in our grid. This project used bilinear interpolation to calculate the rate of theft at each bicycle rack. This process is accomplished by grabbing the four points that make a square around one of our bicycle racks and then performing interpolation in both the X and Y directions of the square. 

This process gives us the rate of theft at each bicycle rack and lets us compare each racks’ theft rate to one another.

With each bicycle racks’ theft rate known we can help users make more informed decisions on where to park their bicycles.            

Potential areas of improvement for this project: 

-Currently we’re only looking at the average rate of theft across the eight year period which doesn’t account for improvements in safety over time. A potential fix would be to develop a system that accounts for changes in theft rate month to month. Look at LSTM neural nets. 

-The blanket occupancy rate of 30% could be tweaked by neighborhood, time of year, and weather to give a more accurate estimation of bicycles in an area over time. 

-Having the same occupancy rate for street corners (sign poles) as bicycle racks could also be tweaked. 

-We're also not accounting for the two leap years that would adjusted our total number of parked bicycles slightly. 


Brief description of scripts in repo

-bike_grid_calc.py:  Calculates and writes the number of street corners, bicycle racks, and bicycle thefts in each square to DB.

-bilinearinter.py: Performs bilinear interpolation calculating the rate of theft of a point using the four points surrounding it that make a square. 

-nearest_nieghbor_grid.py: Performs a nearest neighbor search to see if a squares’ neighbors contain useful data. Used to trim size of database by dropping areas of map where useful data wasn’t present. 

-rack_score_interpo.py: Uses bilinearinter.py and square_check.py to calculate the rate of theft at each bicycle rack and write value to DB. 

-square_check.py: Pulls closest points out of the point field surrounding a rack and finds the four that make a square. 

-theft_grid_score.py: Calculates the rate of theft at a squares center point using the process described above. 

-userlocation.py: A script that takes a user created object and returns a list of bicycle racks and their scores withing a given distance of a user. 


