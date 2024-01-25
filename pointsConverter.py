from constants import *


def translateEvent(eventNum):
    if eventNum == 1:
        return """\n
    sPneumatics.toggleLeftWing();"""
    elif eventNum == 2:
        return """\n
	sPneumatics.toggleRightWing();"""
    elif eventNum == 3:
        return """\n
	sPneumatics.toggleLeftBackWing();"""
    elif eventNum == 4:
        return """\n
	sPneumatics.toggleRightBackWing();"""
    elif eventNum == 5:
        return """\n
	sIntake.moveVoltage(8000);"""
    elif eventNum == 6:
        return """\n
	sIntake.moveVoltage(0);"""
    elif eventNum == 7:
        return """\n
	sIntake.moveVoltage(-8000);"""


def converter(robotInfo, splineData, points, updateSplinesOnly=False):
    events = sorted(splineData[4])
    robotTheta = float(robotInfo[1]) / 180 * pi

    ranges = []
    startIndex = None
    for i, isLine in enumerate(splineData[5]):
        if not isLine and startIndex is None:
            startIndex = i
        if isLine and startIndex is not None:
            ranges.append((startIndex, i - 1))
            startIndex = None

    if startIndex is not None:
        ranges.append((startIndex, len(splineData[5]) - 1))

    currentEvent = 0
    for i, r in enumerate(ranges):
        start = r[0] * (precision + 1)
        end = (r[1] + 1) * (precision + 1)

        # Skip all events that are not on this spline
        while currentEvent < len(events) and events[currentEvent][0] < start: currentEvent += 1

        with open(fr"{PATH_FOR_POINTS_HEADER_FILE_EXPORT}{robotInfo[2]}_spline{i + 1}.h", "w") as output:
            output.write("""#pragma once

#ifndef GENERATED_PATH_DEFS
#define GENERATED_PATH_DEFS
#include <array>
namespace fttbtkjfk {
    struct GeneratedPoint {
        double time;
        
        xstruct {
            double x, y, heading;
        } pose;
        
        double vel;
        double curv;
        int event;
    };
}// namespace fttbtkjfk
#endif
inline auto """ + robotInfo[2] + f"_spline{i + 1}" + """ = std::to_array<fttbtkjfk::GeneratedPoint>({""")
            # Write out the points
            for p in range(start, end):
                x = points[p][0]
                y = points[p][1]

                curv = points[p][2]

                rotatedX = x * cos(-robotTheta) - y * sin(-robotTheta)
                rotatedY = x * sin(-robotTheta) + y * cos(-robotTheta)
                rotatedX += robotInfo[0][0]
                rotatedY += robotInfo[0][1]

                event = 0
                if events and currentEvent < len(events):
                    if p == events[currentEvent][0]:
                        event = events.pop(currentEvent)[1]

                points[p] = (rotatedX, rotatedY)
                output.write(f"{{.time=0,.pose={{.x={rotatedX},.y={rotatedY}}},.curv={1 / curv},.event={event}}}")

                if p < end - 1:
                    output.write(",")

            output.write("});")

    # Terminate here if we are only updating the splines values
    if updateSplinesOnly:
        return

    # Here we build the auton file
    with open(fr"{PATH_FOR_POINTS_HEADER_FILE_EXPORT}{robotInfo[2]}_auton.cpp", "w") as fout:
        fout.write("""#include "Drive.h"
#include "Intake.h"
#include "Logger.h"
#include "Odometry.h"
#include "Pneumatics.h"
#include "Puncher.h"
#include "autons.h"\n""" + "".join([f'#include "autons/{robotInfo[2]}_spline{x + 1}.h"\n' for x in range(len(ranges))]) + """#include "lib/physics/NullMotion.h"
#include "lib/physics/OpControlMotion.h"
#include "lib/physics/PIDTurn.h"
#include "lib/physics/ProfiledMotion.h"
#include "lib/physics/PursuitMotion.h"
#include "lib/physics/TimedMotion.h"
#include "lib/utils/Math.h"
#include "pros/misc.h"
#include "pros/motors.h"
#include "pros/rtos.h"
#include "pros/rtos.hpp"

static LoggerPtr logger;
void """ + robotInfo[2] + """Auton() {
	logger = sLogger.createSource(\"""" + str(robotInfo[2]).capitalize() + """ Auton");
	sDrive.setBrakeMode(pros::E_MOTOR_BRAKE_BRAKE);

	double P = 123;
	double I = 20;
	double D = 500;
	
	double turnAmount;
	""")

        # Write all auton functions
        lineIndex = 0
        splineIndex = 0
        for i, isLine in enumerate(splineData[5]):
            endPointIndex = (i + 1) * (precision + 1)
            startPointIndex = i * (precision + 1)
            if isLine:
                # ADD EVENTS HERE AND AFTER

                # If the event is on the first half of the line we run the event before the movement
                while events and events[0][0] < endPointIndex - (precision + 1) / 2:
                    fout.write(translateEvent(events.pop(0)[1]))

                lineIndex += 1
                fout.write(f"""
    
    Pose point{lineIndex} = Pose({points[endPointIndex][0]}, {points[endPointIndex][1]});
	turnAmount = util::normalize(sOdom.getCurrentState().position.headingToPoint(point{lineIndex}) / M_PI * 180{" + 180" if splineData[6][i] else ""}, 360.0);
	sDrive.setCurrentMotion(PIDTurn(turnAmount, PID(P + 50, I, D, true, 3)));
	sDrive.waitUntilSettled(1000);
	
	sDrive.setCurrentMotion(ProfiledMotion({"-" if splineData[6][i] else ""}sOdom.getCurrentState().position.distanceTo(point{lineIndex}), 60, 60, 100));
	sDrive.waitUntilSettled(2500);""")

                # If the event is on the second half of the line we run the event after the movement
                while events and events[0][0] <= endPointIndex:
                    fout.write(translateEvent(events.pop(0)[1]))

            elif (i != 0 and splineData[5][i - 1]) or i == 0:
                splineIndex += 1
                # We turn robot to point that is at the beginning of the spline
                # (we choose point 15% of the way along the first curve (kinda arbitrary)
                fout.write(f"""

    Pose lookAhead{splineIndex} = Pose({points[int(startPointIndex + 0.15 * precision)][0]}, {points[int(startPointIndex + 0.15 * precision)][1]});
    turnAmount = util::normalize(sOdom.getCurrentState().position.headingToPoint(lookAhead{splineIndex}) / M_PI * 180{" + 180" if splineData[6][i] else ""}, 360.0);
    sDrive.setCurrentMotion(PIDTurn(turnAmount, PID(P + 50, I, D, true, 3)));
    sDrive.waitUntilSettled(1000);""")

                fout.write(f"""
    
    sDrive.setCurrentMotion(PursuitMotion({robotInfo[2] + f"_spline{splineIndex}"}, 12, 40, 50, {str(splineData[6][i]).lower()}));
	sDrive.waitUntilSettled(8000);
	sDrive.setCurrentMotion(NullMotion(true));""")

        fout.write("""
        
        
    sDrive.setBrakeMode(pros::E_MOTOR_BRAKE_COAST);
    sDrive.setCurrentMotion(OpControlMotion());
}""")


if __name__ == "__main__":
    converter()
