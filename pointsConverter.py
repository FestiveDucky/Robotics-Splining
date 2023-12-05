import math


def converter():
    # Current angle of the robot
    try:
        robotAngle = float(input("Enter robot angle: "))

        # Current position of the robot
        robotX = float(input("Enter robot x coordinate: "))
        robotY = float(input("Enter robot y coordinate: "))
    except ValueError:
        print("Invalid characters for robot pose!")
        return

    robotTheta = float(robotAngle) / 180 * math.pi
    with open("points.txt", "r") as file:
        with open("points.h", "w") as output:
            output.write("""#pragma once

#ifndef GENERATED_PATH_DEFS
#define GENERATED_PATH_DEFS
#include <array>
namespace fttbtkjfk {
    struct GeneratedPoint {
        double time;
        struct {
            double x, y, heading;
        } pose;
        struct {
            double left, right;
        } wheelVels;
        double vel, accel, curv;
    };
}// namespace fttbtkjfk
#endif
inline auto points = std::to_array<fttbtkjfk::GeneratedPoint>({""")

            count = len(file.readlines())
            file.seek(0)

            for index, line in enumerate(file):
                tokens = line.split(" ")
                for i in range(len(tokens)):
                    tokens[i] = float(tokens[i])
                # temporary multiply by -1 because right now, going right is -x
                x = tokens[0] + robotX
                y = tokens[1] + robotY

                curv = tokens[2]

                rotatedX = x * math.cos(-robotTheta) - y * math.sin(-robotTheta)
                rotatedY = x * math.sin(-robotTheta) + y * math.cos(-robotTheta)

                output.write(f"{{.time=0,.pose={{.x={rotatedX},.y={rotatedY}}},.curv={1 / curv}}}")

                if index < (count - 1):
                    output.write(",")

                print(f"{rotatedX} {rotatedY}")

            output.write("});")


if __name__ == "__main__":
    converter()