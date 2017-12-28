#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "Aleksey Lobanov"
__copyright__ = "Copyright 2017, Aleksey Lobanov"
__credits__ = ["Aleksey Lobanov"]
__license__ = "GPL v3"
__version__ = "1.9"
__maintainer__ = "Aleksey Lobanov"
__email__ = "i@likemath.ru"

import sys
import re

import pylab as pl
import numpy as np
from scipy.optimize import minimize


DATA_FILE_NAME = "temperature.txt"

# groups: hours, minutes, seconds, container_id, temperature
re_line = re.compile(r"(\d+):(\d+):(\d+)\s+(\d):\s+([\d.]+)")


def get_error_function(arr):
    X = np.asarray([x[0] for x in arr])
    Y = np.asarray([x[1] for x in arr])

    def cont_err(x, *args):
        """
        T(t) = A + B*exp(-C*x)
        where A,B,C > 0
        """
        A, B, C, = x

        return ((A+B*np.exp(-C*X) - Y)**2).sum()
    return cont_err


def get_best_params(arr):
    """
    Assume T(t) = A + B*exp(-C*x)
    Returns B and C, not A because it is just shift
    """
    min_res = minimize(
        get_error_function(arr),
        [0.1, 0.1, 0.1],
        bounds=[(0.1, 100), (1, 100), (1e-4, 1e-2)]
    )
    assert(min_res.success)
    return float(min_res.x[1]), float(min_res.x[2])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        DATA_FILE_NAME = sys.argv[1]

    containers = {}

    with open(DATA_FILE_NAME) as f_data:
        for line in f_data:
            line = line.strip()
            if not line:
                continue

            line_vals = re_line.findall(line)[0]
            hours = int(line_vals[0])
            minutes = int(line_vals[1])
            seconds = int(line_vals[2])
            container_id = int(line_vals[3])
            temperature = float(line_vals[4])

            time = hours*60**2 + minutes*60 + seconds
            if container_id not in containers:
                containers[container_id] = []
            containers[container_id].append((time, temperature))
        for key in containers:
            containers[key] = [
                (x[0] - containers[key][0][0], x[1]) for x in containers[key]
            ]

    plot_lines = []
    for key in containers:
        B, C = get_best_params(containers[key])
        print("params for {}: {}, {}".format(key, B, C))
        cur_line, = pl.plot(
            [x[0] for x in containers[key]],
            [x[1] for x in containers[key]],
            label="{}: {:2.1f}, {:.5f}".format(key, B, C),
            marker="o"
        )
        plot_lines.append(cur_line)
    pl.xlabel("Time, s")
    pl.ylabel("Temperature, °C")
    pl.legend(handles=plot_lines)
    pl.savefig("plot.svg")
