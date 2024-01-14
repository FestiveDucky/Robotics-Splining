from constants import *


def converter(robotInfo, events):
    events = sorted(events)
    robotTheta = float(robotInfo[1]) / 180 * pi
    with open("points.txt", "r") as file:
        with open(fr"{PATH_FOR_POINTS_HEADER_FILE_EXPORT}{robotInfo[2]}.h", "w") as output:
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
        int event;
    };
}// namespace fttbtkjfk
#endif
inline auto """ + robotInfo[2] + """ = std::to_array<fttbtkjfk::GeneratedPoint>({""")

            count = len(file.readlines())
            file.seek(0)

            for index, line in enumerate(file):
                tokens = line.split(" ")
                for i in range(len(tokens)):
                    tokens[i] = float(tokens[i])

                x = tokens[0]
                y = tokens[1]

                curv = tokens[2]

                rotatedX = x * cos(-robotTheta) - y * sin(-robotTheta)
                rotatedY = x * sin(-robotTheta) + y * cos(-robotTheta)
                rotatedX += robotInfo[0][0]
                rotatedY += robotInfo[0][1]

                event = 0
                if events:
                    print(events)
                    if index == events[0][0]:
                        event = events.pop(0)[1]

                output.write(f"{{.time=0,.pose={{.x={rotatedX},.y={rotatedY}}},.curv={1 / curv}}},.event={event}")

                if index < (count - 1):
                    output.write(",")

                print(f"{rotatedX} {rotatedY}")

            output.write("});")


if __name__ == "__main__":
    converter()