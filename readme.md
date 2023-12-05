Required Python Packages: Pygame, Pillow

The save.txt file stores the saved state of your instance of the spline generator. The first line stores the resolution of your screen so that the points saved can be resized for different sizes, the second line stores the control points of the spline and the last line stores the obstacle points. I reccomend not to touch the obstacle points since they are already set up. In the worst case, there is a backup of the obstacles in the main.py file at the top.

Guide:
-
- Run main.py and create your spline
- Press e to export your points and press s to save your spline for later (if you want)
- Open the terminal/console where you ran main.py, and fill out the prompts for about the robot pose, enter the values (default ones are all 0)
- There should now be a "points.h" file in the same directory as the spline generator move it to your auton folder next to "skillsAuton.cpp"
- Then just import the file and use the "points" array in your pursuit motion


Controls:
-
- p: adds a new curve with the end point being at your mouse position
- r: removes the most recent curve added
- s: saves the instance of the generator to the save.txt file
- e: exports the points and curvatures of the spline to points.txt
- o: adds an obstacle point
- DELETE: removes an obstacle point
- SPACE: Manually updates the screen


Note if your device has a resolution of less than 1.3 (most people don't), it sucks to suck and this won't work properly :)