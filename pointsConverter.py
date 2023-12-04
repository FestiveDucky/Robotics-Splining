import sys
import math
import os

# python3 pointsConverter.py points.txt 0 0 0
def main():
    if len(sys.argv) < 5:
        print("Specify input path")
        return

    if sys.argv[1] == '-h' or sys.argv[1] == "--help":
        print("pathFile robotX robotY robotHeading")
        return

    robotX = float(sys.argv[2])
    robotY = float(sys.argv[3])
    robotTheta = float(sys.argv[4]) / 180 * math.pi

    with open(sys.argv[1], "r") as file:
        with open(sys.argv[1].split(".")[0] + ".h", "w") as output:
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
inline auto """ + sys.argv[1].split(".")[0] + " = std::to_array<fttbtkjfk::GeneratedPoint>({")

            count = len(file.readlines())
            file.seek(0)

            for index, line in enumerate(file):
                tokens = line.split(" ")
                for i in range(len(tokens)):
                    tokens[i] = float(tokens[i])
                # temporary multiply by -1 because right now, going right is -x
                x = tokens[1]
                y = tokens[0]
                curv = tokens[2]

                rotatedX = x * math.cos(-robotTheta) - y * math.sin(-robotTheta)
                rotatedY = x * math.sin(-robotTheta) + y * math.cos(-robotTheta)

                output.write(f"{{.time=0,.pose={{.x={rotatedX},.y={rotatedY}}},.curv={1 / curv}}}")

                if index < (count - 1):
                    output.write(",")

                print(f"{rotatedX} {rotatedY}")

            output.write("});")


if __name__ == "__main__":
    main()