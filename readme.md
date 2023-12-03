Required Python Packages: Pygame, Pillow

The save.txt file stores the saved state of your instance of the spline generator. The first line stores the resolution of your screen so that the points saved can be resized for different sizes, the second line stores the control points of the spline and the last line stores the obstacle points. I reccomend not to touch the obstacle points since they are already set up. In the worst case, there is a backup of the obstacles in the main.py file at the top.

Controls:
-
- p: adds a new curve with the end point being at your mouse position
- r: removes the most recent curve added
- s: saves the instance of the generator to the save.txt file
- e: exports the points and curvatures of the spline to points.txt
- o: adds an obstacle point
- DELETE: removes an obstacle point
- SPACE: Manually updates the screen