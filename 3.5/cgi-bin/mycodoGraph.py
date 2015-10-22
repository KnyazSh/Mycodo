#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  mycodoGraph.py - Mycodo Graph Module
#
#  Copyright (C) 2015  Kyle T. Gabriel
#
#  This file is part of Mycodo
#
#  Mycodo is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Mycodo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Mycodo. If not, see <http://www.gnu.org/licenses/>.
#
#  Contact at kylegabriel.com

install_directory = "/var/www/mycodo"

import datetime
import fileinput
import logging
import os
import subprocess
import time
from lockfile import LockFile

log_path = "%s/log" % install_directory # Where generated logs are stored
image_path = "%s/images" % install_directory # Where generated graphs are stored

# Logs that are on the tempfs and are written to every sensor read
sensor_t_log_file_tmp = "%s/sensor-t-tmp.log" % log_path
sensor_ht_log_file_tmp = "%s/sensor-ht-tmp.log" % log_path
sensor_co2_log_file_tmp = "%s/sensor-co2-tmp.log" % log_path
sensor_press_log_file_tmp = "%s/sensor-press-tmp.log" % log_path
relay_log_file_tmp = "%s/relay-tmp.log" % log_path

# Logs that are periodically concatenated (every 6 hours) to the SD card
sensor_t_log_file = "%s/sensor-t.log" % log_path
sensor_ht_log_file = "%s/sensor-ht.log" % log_path
sensor_co2_log_file = "%s/sensor-co2.log" % log_path
sensor_press_log_file = "%s/sensor-press.log" % log_path
relay_log_file = "%s/relay.log" % log_path

# Lockfiles
lock_directory = "/var/lock/mycodo"
relay_log_lock_path = "%s/relay" % lock_directory
sensor_t_log_lock_path = "%s/sensor-t-log" % lock_directory
sensor_ht_log_lock_path = "%s/sensor-ht-log" % lock_directory
sensor_co2_log_lock_path = "%s/sensor-co2-log" % lock_directory
sensor_press_log_lock_path = "%s/sensor-press-log" % lock_directory

#################################################
#                Graph Generation               #
#################################################

# Generate gnuplot graph
def generate_graph(sensor_type, graph_type, graph_span, graph_id, sensor_number, sensor_t_name, sensor_t_graph, sensor_t_period, sensor_t_yaxis_relay_min, sensor_t_yaxis_relay_max, sensor_t_yaxis_relay_tics, sensor_t_yaxis_relay_mtics, sensor_t_yaxis_temp_min, sensor_t_yaxis_temp_max, sensor_t_yaxis_temp_tics, sensor_t_yaxis_temp_mtics, sensor_t_temp_relays_up_list, sensor_t_temp_relays_down_list, pid_t_temp_relay_high, pid_t_temp_relay_low, sensor_ht_name, sensor_ht_graph, sensor_ht_period, sensor_ht_yaxis_relay_min, sensor_ht_yaxis_relay_max, sensor_ht_yaxis_relay_tics, sensor_ht_yaxis_relay_mtics, sensor_ht_yaxis_temp_min, sensor_ht_yaxis_temp_max, sensor_ht_yaxis_temp_tics, sensor_ht_yaxis_temp_mtics, sensor_ht_yaxis_hum_min, sensor_ht_yaxis_hum_max, sensor_ht_yaxis_hum_tics, sensor_ht_yaxis_hum_mtics, sensor_ht_temp_relays_up_list, sensor_ht_temp_relays_down_list, sensor_ht_hum_relays_up_list, sensor_ht_hum_relays_down_list, pid_ht_temp_relay_high, pid_ht_temp_relay_low, pid_ht_hum_relay_high, pid_ht_hum_relay_low, sensor_co2_name, sensor_co2_graph, sensor_co2_period, sensor_co2_yaxis_relay_min, sensor_co2_yaxis_relay_max, sensor_co2_yaxis_relay_tics, sensor_co2_yaxis_relay_mtics, sensor_co2_yaxis_co2_min, sensor_co2_yaxis_co2_max, sensor_co2_yaxis_co2_tics, sensor_co2_yaxis_co2_mtics, sensor_co2_relays_up_list, sensor_co2_relays_down_list, pid_co2_relay_high, pid_co2_relay_low, sensor_press_name, sensor_press_graph, sensor_press_period, sensor_press_yaxis_relay_min, sensor_press_yaxis_relay_max, sensor_press_yaxis_relay_tics, sensor_press_yaxis_relay_mtics, sensor_press_yaxis_temp_min, sensor_press_yaxis_temp_max, sensor_press_yaxis_temp_tics, sensor_press_yaxis_temp_mtics, sensor_press_yaxis_press_min, sensor_press_yaxis_press_max, sensor_press_yaxis_press_tics, sensor_press_yaxis_press_mtics, sensor_press_temp_relays_up_list, sensor_press_temp_relays_down_list, sensor_press_press_relays_up_list, sensor_press_press_relays_down_list, pid_press_temp_relay_high, pid_press_temp_relay_low, pid_press_press_relay_high, pid_press_press_relay_low, relay_name, relay_pin, time_from, time_to, width, combined_temp_relays, combined_temp_min, combined_temp_max, combined_temp_tics, combined_temp_mtics, combined_hum_relays, combined_hum_min, combined_hum_max, combined_hum_tics, combined_hum_mtics, combined_co2_relays, combined_co2_min, combined_co2_max, combined_co2_tics, combined_co2_mtics, combined_press_relays, combined_press_min, combined_press_max, combined_press_tics, combined_press_mtics):

    sensor_t_log_final = [0] * (len(sensor_t_name)+1)
    sensor_ht_log_final = [0] * (len(sensor_ht_name)+1)
    sensor_co2_log_final = [0] * (len(sensor_co2_name)+1)
    sensor_press_log_final = [0] * (len(sensor_press_name)+1)

    tmp_path = "/var/tmp"
    h = 0
    d = 0
    seconds = None
    cmd = None

    # Calculate a past date from a number of hours or days ago
    if graph_span == "1h":
        h = 1
        seconds = 3600
        time_ago = '1 Hour'
    elif graph_span == "3h":
        h = 3
        seconds = 10800
        time_ago = '3 Hours'
    elif graph_span == "6h":
        h = 6
        seconds = 21600
        time_ago = '6 Hours'
    elif graph_span == "12h":
        h = 12
        seconds = 43200
        time_ago = '12 Hours'
    elif graph_span == "1d" or graph_span == "default":
        d = 1
        seconds = 86400
        time_ago = '1 Day'
    elif graph_span == "3d":
        d = 3
        seconds = 259200
        time_ago = '3 Days'
    elif graph_span == "1w":
        d = 7
        seconds = 604800
        time_ago = '1 Week'
    elif graph_span == "2w":
        d = 14
        seconds = 1209600
        time_ago = '2 Weeks'
    elif graph_span == "1m":
        d = 30
        seconds = 2592000
        time_ago = '1 Month'
    elif graph_span == "3m":
        d = 90
        seconds = 7776000
        time_ago = '3 Months'
    elif graph_span == "6m":
        d = 180
        seconds = 15552000
        time_ago = '6 Months'
    elif graph_span == "legend-full":
        h = 6
        seconds = 21600
        time_ago = '6 Hours'

    if time_from != None and time_to != None:
        date_ago = time.strftime('%Y %m %d %H %M %S', time.localtime(float(time_from)))
        date_now = time.strftime('%Y %m %d %H %M %S', time.localtime(float(time_to)))
        date_ago_disp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(float(time_from)))
        date_now_disp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(float(time_to)))
        time_ago = "Custom Time"
        seconds = 15552000
    else:
        date_now = datetime.datetime.now().strftime("%Y %m %d %H %M %S")
        date_now_disp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        date_ago = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y %m %d %H %M %S")
        date_ago_disp = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%d/%m/%Y %H:%M:%S")

    if not os.path.exists(lock_directory):
        os.makedirs(lock_directory)

    lock = LockFile(relay_log_lock_path)

    while not lock.i_am_locking():
        try:
            logging.debug("[Generate Graph] Acquiring Lock: %s", lock.path)
            lock.acquire(timeout=60)    # wait up to 60 seconds
        except:
            logging.warning("[Generate Graph] Breaking Lock to Acquire: %s", lock.path)
            lock.break_lock()
            lock.acquire()

    logging.debug("[Generate Graph] Gained lock: %s", lock.path)

    # Combine relay logs
    relay_log_files_combine = [relay_log_file, relay_log_file_tmp]
    relay_log_generate = "%s/relay-logs-combined.log" % tmp_path
    with open(relay_log_generate, 'w') as fout:
        for line in fileinput.input(relay_log_files_combine):
            fout.write(line)

    logging.debug("[Generate Graph] Removing lock: %s", lock.path)
    lock.release()

    # Concatenate default and separate logs
    if graph_span == 'default' or graph_type == 'separate':
        if graph_type == 'separate':
            generate_type = 'separate'
        if graph_span == 'default':
            generate_type = 'default'

        if sensor_type == 't':
            if not os.path.exists(lock_directory):
                os.makedirs(lock_directory)

            lock = LockFile(sensor_t_log_lock_path)
            while not lock.i_am_locking():
                try:
                    logging.debug("[Generate Graph] Acquiring Lock: %s", lock.path)
                    lock.acquire(timeout=60)    # wait up to 60 seconds
                except:
                    logging.warning("[Generate Graph] Breaking Lock to Acquire: %s", lock.path)
                    lock.break_lock()
                    lock.acquire()

            logging.debug("[Generate Graph] Gained lock: %s", lock.path)

            filenames = [sensor_t_log_file, sensor_t_log_file_tmp]
            sensor_t_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 't', generate_type)
            with open(sensor_t_log_generate, 'w') as outfile:
                for fname in filenames:
                    with open(fname) as infile:
                        for line in infile:
                            outfile.write(line)

            logging.debug("[Generate Graph] Removing lock: %s", lock.path)
            lock.release()

        if sensor_type == 'ht':
            if not os.path.exists(lock_directory):
                os.makedirs(lock_directory)

            lock = LockFile(sensor_ht_log_lock_path)
            while not lock.i_am_locking():
                try:
                    logging.debug("[Generate Graph] Acquiring Lock: %s", lock.path)
                    lock.acquire(timeout=60)    # wait up to 60 seconds
                except:
                    logging.warning("[Generate Graph] Breaking Lock to Acquire: %s", lock.path)
                    lock.break_lock()
                    lock.acquire()

            logging.debug("[Generate Graph] Gained lock: %s", lock.path)

            filenames = [sensor_ht_log_file, sensor_ht_log_file_tmp]
            sensor_ht_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 'ht', generate_type)
            with open(sensor_ht_log_generate, 'w') as outfile:
                for fname in filenames:
                    with open(fname) as infile:
                        for line in infile:
                            outfile.write(line)

            logging.debug("[Generate Graph] Removing lock: %s", lock.path)
            lock.release()

        if sensor_type == 'co2':
            if not os.path.exists(lock_directory):
                os.makedirs(lock_directory)

            lock = LockFile(sensor_co2_log_lock_path)
            while not lock.i_am_locking():
                try:
                    logging.debug("[Write CO2 Sensor Log] Acquiring Lock: %s", lock.path)
                    lock.acquire(timeout=60)    # wait up to 60 seconds
                except:
                    logging.warning("[Write CO2 Sensor Log] Breaking Lock to Acquire: %s", lock.path)
                    lock.break_lock()
                    lock.acquire()

            logging.debug("[Write CO2 Sensor Log] Gained lock: %s", lock.path)

            filenames = [sensor_co2_log_file, sensor_co2_log_file_tmp]
            sensor_co2_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 'co2', generate_type)
            with open(sensor_co2_log_generate, 'w') as outfile:
                for fname in filenames:
                    with open(fname) as infile:
                        for line in infile:
                            outfile.write(line)

            logging.debug("[Generate Graph] Removing lock: %s", lock.path)
            lock.release()

        if sensor_type == 'press':
            if not os.path.exists(lock_directory):
                os.makedirs(lock_directory)

            lock = LockFile(sensor_press_log_lock_path)
            while not lock.i_am_locking():
                try:
                    logging.debug("[Generate Graph] Acquiring Lock: %s", lock.path)
                    lock.acquire(timeout=60)    # wait up to 60 seconds
                except:
                    logging.warning("[Generate Graph] Breaking Lock to Acquire: %s", lock.path)
                    lock.break_lock()
                    lock.acquire()

            logging.debug("[Generate Graph] Gained lock: %s", lock.path)

            filenames = [sensor_press_log_file, sensor_press_log_file_tmp]
            sensor_press_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 'press', generate_type)
            with open(sensor_press_log_generate, 'w') as outfile:
                for fname in filenames:
                    with open(fname) as infile:
                        for line in infile:
                            outfile.write(line)

            logging.debug("[Generate Graph] Removing lock: %s", lock.path)
            lock.release()

    # Parse default logs
    if graph_span == "default":
        if sensor_type == "t":
            sensor_t_log_generate = "%s/sensor-%s-logs-%s.log" % (
                tmp_path, sensor_type, graph_span)
            lines = 86400
            sensor_t_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s-day.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_t_log_generate, sensor_t_log_final[0])
            logging.debug("[Generate Graph] cmd: %s", cmd)
            os.system(cmd)

            lines = 604800
            sensor_t_log_final[1] = "%s/sensor-%s-logs-%s-%s-%s-week.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_t_log_generate, sensor_t_log_final[1])

        if sensor_type == "ht":
            sensor_ht_log_generate = "%s/sensor-%s-logs-%s.log" % (
                tmp_path, sensor_type, graph_span)
            lines = 86400
            sensor_ht_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s-day.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_ht_log_generate, sensor_ht_log_final[0])
            logging.debug("[Generate Graph] cmd: %s", cmd)
            os.system(cmd)

            lines = 604800
            sensor_ht_log_final[1] = "%s/sensor-%s-logs-%s-%s-%s-week.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_ht_log_generate, sensor_ht_log_final[1])

        if sensor_type == "co2":
            sensor_co2_log_generate = "%s/sensor-%s-logs-%s.log" % (
                tmp_path, sensor_type, graph_span)
            lines = 86400
            sensor_co2_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s-day.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_co2_log_generate, sensor_co2_log_final[0])
            logging.debug("[Generate Graph] cmd: %s", cmd)
            os.system(cmd)

            lines = 604800
            sensor_co2_log_final[1] = "%s/sensor-%s-logs-%s-%s-%s-week.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_co2_log_generate, sensor_co2_log_final[1])

        if sensor_type == "press":
            sensor_press_log_generate = "%s/sensor-%s-logs-%s.log" % (
                tmp_path, sensor_type, graph_span)
            lines = 86400
            sensor_press_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s-day.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_press_log_generate, sensor_press_log_final[0])
            logging.debug("[Generate Graph] cmd: %s", cmd)
            os.system(cmd)

            lines = 604800
            sensor_press_log_final[1] = "%s/sensor-%s-logs-%s-%s-%s-week.log" %  (
                tmp_path, sensor_type, graph_span, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_press_log_generate, sensor_press_log_final[1])

        logging.debug("[Generate Graph] cmd: %s", cmd)
        os.system(cmd)

    # Parse separate logs
    elif graph_type == "separate":
        sensor_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, sensor_type, graph_type)
        if sensor_type == "t":
            lines = seconds/sensor_t_period[int(sensor_number)]
            sensor_t_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s.log" % (
                tmp_path, sensor_type, graph_type, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_log_generate, sensor_t_log_final[0])

        if sensor_type == "ht":
            lines = seconds/sensor_ht_period[int(sensor_number)]
            sensor_ht_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s.log" % (
                tmp_path, sensor_type, graph_type, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_log_generate, sensor_ht_log_final[0])

        if sensor_type == "co2":
            lines = seconds/sensor_co2_period[int(sensor_number)]
            sensor_co2_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s.log" % (
                tmp_path, sensor_type, graph_type, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_log_generate, sensor_co2_log_final[0])

        if sensor_type == "press":
            lines = seconds/sensor_press_period[int(sensor_number)]
            sensor_press_log_final[0] = "%s/sensor-%s-logs-%s-%s-%s.log" % (
                tmp_path, sensor_type, graph_type, graph_id, sensor_number)
            cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                sensor_number, sensor_type, lines, sensor_log_generate, sensor_press_log_final[0])

        logging.debug("[Generate Graph] cmd: %s", cmd)
        os.system(cmd)

    # Concatenate combined logs
    elif graph_type == "combined":
        if sum(sensor_t_graph):
            sensor_t_log_files_combine = [sensor_t_log_file, sensor_t_log_file_tmp]
            sensor_t_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 't', graph_type)
            with open(sensor_t_log_generate, 'w') as fout:
                for line in fileinput.input(sensor_t_log_files_combine):
                    fout.write(line)
        else:
            sensor_t_log_generate = None

        if sum(sensor_ht_graph):
            sensor_ht_log_files_combine = [sensor_ht_log_file, sensor_ht_log_file_tmp]
            sensor_ht_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 'ht', graph_type)
            with open(sensor_ht_log_generate, 'w') as fout:
                for line in fileinput.input(sensor_ht_log_files_combine):
                    fout.write(line)
        else:
            sensor_ht_log_generate = None

        if sum(sensor_co2_graph):
            sensor_co2_log_files_combine = [sensor_co2_log_file, sensor_co2_log_file_tmp]
            sensor_co2_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 'co2', graph_type)
            with open(sensor_co2_log_generate, 'w') as fout:
                for line in fileinput.input(sensor_co2_log_files_combine):
                    fout.write(line)
        else:
            sensor_co2_log_generate = None

        if sum(sensor_press_graph):
            sensor_press_log_files_combine = [sensor_press_log_file, sensor_press_log_file_tmp]
            sensor_press_log_generate = "%s/sensor-%s-logs-%s.log" % (tmp_path, 'press', graph_type)
            with open(sensor_press_log_generate, 'w') as fout:
                for line in fileinput.input(sensor_press_log_files_combine):
                    fout.write(line)
        else:
            sensor_press_log_generate = None

        time.sleep(0.1) # Allow sensor log to be completely written before modification and use

        for i in range(0, len(sensor_t_name)):
            lines = seconds/sensor_t_period[i]
            if sensor_t_graph[i]:
                sensor_t_log_final[i] = "%s/sensor-%s-logs-%s-%s-%s.log" %  (
                    tmp_path, 't', graph_type, graph_id, i)
                cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                    i, 't', lines, sensor_t_log_generate, sensor_t_log_final[i])
                logging.debug("[Generate Graph] cmd: %s", cmd)
                os.system(cmd)

        for i in range(0, len(sensor_ht_name)):
            lines = seconds/sensor_ht_period[i]
            if sensor_ht_graph[i]:
                sensor_ht_log_final[i] = "%s/sensor-%s-logs-%s-%s-%s.log" %  (
                    tmp_path, 'ht', graph_type, graph_id, i)
                cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                    i, 'ht', lines, sensor_ht_log_generate, sensor_ht_log_final[i])
                logging.debug("[Generate Graph] cmd: %s", cmd)
                os.system(cmd)

        for i in range(0, len(sensor_co2_name)):
            lines = seconds/sensor_co2_period[i]
            if sensor_co2_graph[i]:
                sensor_co2_log_final[i] = "%s/sensor-%s-logs-%s-%s-%s.log" %  (
                    tmp_path, 'co2', graph_type, graph_id, i)
                cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                    i, 'co2', lines, sensor_co2_log_generate, sensor_co2_log_final[i])
                logging.debug("[Generate Graph] cmd: %s", cmd)
                os.system(cmd)

        for i in range(0, len(sensor_press_name)):
            lines = seconds/sensor_press_period[i]
            if sensor_press_graph[i]:
                sensor_press_log_final[i] = "%s/sensor-%s-logs-%s-%s-%s.log" %  (
                    tmp_path, 'press', graph_type, graph_id, i)
                cmd = "/var/www/mycodo/cgi-bin/log-parser.sh %s %s %s %s %s" % (
                    i, 'press', lines, sensor_press_log_generate, sensor_press_log_final[i])
                logging.debug("[Generate Graph] cmd: %s", cmd)
                os.system(cmd)


    logging.debug("[Generate Graph] Generating Graph...")

    # Write the following output to a file that will be executed with gnuplot
    gnuplot_graph = "%s/plot-%s-%s-%s-%s-%s.gnuplot" % (
        tmp_path, sensor_type, graph_type, graph_span, graph_id, sensor_number)
    plot = open(gnuplot_graph, 'w')

    plot.write('reset\n')
    plot.write('set xdata time\n')
    plot.write('set timefmt \"%Y %m %d %H %M %S\"\n')

    #
    # Graph image size
    #

    num_graphs = 0

    if bool(sum(sensor_t_graph)):
        num_graphs += 1

    if bool(sum(sensor_ht_graph)):
        if bool(sum(sensor_t_graph)):
            num_graphs += 1
        else:
            num_graphs += 2

    if bool(sum(sensor_co2_graph)):
        num_graphs += 1

    if bool(sum(sensor_press_graph)):
        if bool(sum(sensor_t_graph)) or bool(sum(sensor_ht_graph)):
            num_graphs += 1
        else:
            num_graphs += 2

    sensor_t_graph_relay = 0
    sensor_ht_graph_relay = 0
    sensor_co2_graph_relay = 0
    sensor_press_graph_relay = 0

    if sensor_type == "t":
        if ((len(sensor_t_temp_relays_up_list[int(sensor_number)]) > 1 or (len(sensor_t_temp_relays_up_list[int(sensor_number)]) == 1 and sensor_t_temp_relays_up_list[int(sensor_number)][0] != 0)) or
                (len(sensor_t_temp_relays_down_list[int(sensor_number)]) > 1 or (len(sensor_t_temp_relays_down_list[int(sensor_number)]) == 1 and sensor_t_temp_relays_down_list[int(sensor_number)][0] != 0))):
            sensor_t_graph_relay = 1

    if sensor_type == "ht":
        if ((len(sensor_ht_temp_relays_up_list[int(sensor_number)]) > 1 or (len(sensor_ht_temp_relays_up_list[int(sensor_number)]) == 1 and sensor_ht_temp_relays_up_list[int(sensor_number)][0] != 0)) or
                (len(sensor_ht_temp_relays_down_list[int(sensor_number)]) > 1 or (len(sensor_ht_temp_relays_down_list[int(sensor_number)]) == 1 and sensor_ht_temp_relays_down_list[int(sensor_number)][0] != 0)) or 
                (len(sensor_ht_hum_relays_up_list[int(sensor_number)]) > 1 or (len(sensor_ht_hum_relays_up_list[int(sensor_number)]) == 1 and sensor_ht_hum_relays_up_list[int(sensor_number)][0] != 0)) or
                (len(sensor_ht_hum_relays_down_list[int(sensor_number)]) > 1 or (len(sensor_ht_hum_relays_down_list[int(sensor_number)]) == 1 and sensor_ht_hum_relays_down_list[int(sensor_number)][0] != 0))):
            sensor_ht_graph_relay = 1

    if sensor_type == "co2":
        if ((len(sensor_co2_relays_up_list[int(sensor_number)]) > 1 or (len(sensor_co2_relays_up_list[int(sensor_number)]) == 1 and sensor_co2_relays_up_list[int(sensor_number)][0] != 0)) or
                (len(sensor_co2_relays_down_list[int(sensor_number)]) > 1 or (len(sensor_co2_relays_down_list[int(sensor_number)]) == 1 and sensor_co2_relays_down_list[int(sensor_number)][0] != 0))):
            sensor_co2_graph_relay = 1

    if sensor_type == "press":
        if ((len(sensor_press_temp_relays_up_list[int(sensor_number)]) > 1 or (len(sensor_press_temp_relays_up_list[int(sensor_number)]) == 1 and sensor_press_temp_relays_up_list[int(sensor_number)][0] != 0)) or
                (len(sensor_press_temp_relays_down_list[int(sensor_number)]) > 1 or (len(sensor_press_temp_relays_down_list[int(sensor_number)]) == 1 and sensor_press_temp_relays_down_list[int(sensor_number)][0] != 0)) or 
                (len(sensor_press_press_relays_up_list[int(sensor_number)]) > 1 or (len(sensor_press_press_relays_up_list[int(sensor_number)]) == 1 and sensor_press_press_relays_up_list[int(sensor_number)][0] != 0)) or
                (len(sensor_press_press_relays_down_list[int(sensor_number)]) > 1 or (len(sensor_press_press_relays_down_list[int(sensor_number)]) == 1 and sensor_press_press_relays_down_list[int(sensor_number)][0] != 0))):
            sensor_press_graph_relay = 0
    
    if graph_span == "default":
        graph_width = 1000
        graph_height = 1000
    elif graph_type == "combined":
        graph_width = 1000
        graph_height = (500*num_graphs)
    elif graph_type == "separate":
        if sensor_t_graph_relay or sensor_ht_graph_relay or sensor_co2_graph_relay or sensor_press_graph_relay:
            graph_width = 1000
            graph_height = 800
        else:
            graph_width = 1000
            graph_height = 600

    if width != None:
        graph_width = width

    plot.write('set terminal png size ' + str(graph_width) + ',' + str(graph_height) + '\n')


    #
    # Output file
    #
    if graph_span == 'default':
        graph_type = 'default'

    plot.write('set output \"' + image_path + '/graph-' + sensor_type + graph_type + graph_span + '-' + graph_id + '-' + sensor_number + '.png\"\n')


    #
    # Axes ranges
    #
    y1_min = '0'
    y1_max = '35'

    if sensor_type == "co2":
        y1_min = '0'
        y1_max = '5000'

    plot.write('set xrange [\"' + date_ago + '\":\"' + date_now + '\"]\n')
    plot.write('set format x \"%H:%M\\n%m/%d\"\n')
    plot.write('set yrange [' + y1_min + ':' + y1_max + ']\n')


    #
    # Ticks
    #
    if (((graph_type == "combined" and sum(sensor_t_graph)) and sensor_type == "x") or
        sensor_type == "t"):
        plot.write('set ytics 5\n')
        plot.write('set mytics 5\n')

    elif sensor_type == "ht":
        y2_min = '0'
        y2_max = '100'
        plot.write('set y2range [' + y2_min + ':' + y2_max + ']\n')
        plot.write('set ytics 5\n')
        plot.write('set mytics 5\n')
        plot.write('set y2tics 10\n')
        plot.write('set my2tics 5\n')

    elif sensor_type == "press":
        y2_min = '97000'
        y2_max = '99000'
        plot.write('set y2range [' + y2_min + ':' + y2_max + ']\n')
        plot.write('set ytics 5\n')
        plot.write('set mytics 5\n')
        plot.write('set y2tics 250\n')
        plot.write('set my2tics 5\n')

    elif (((graph_type == "combined" and sum(sensor_co2_graph)) and sensor_type == "x") or
        sensor_type == "co2"):
        plot.write('set ytics 500\n')
        plot.write('set mytics 5\n')
   
    #
    # Styling
    #
    graph_colors = ['#D55E00', '#0072B2', '#009E73',
                    '#7164a3', '#599e86', '#c3ae4f', '#CC79A7', '#957EF9', '#CC8D9C', '#717412', '#0B479B',
                    ]

    plot.write('set tics nomirror\n')
    plot.write('set style line 11 lc rgb \'#808080\' lt 1\n')
    plot.write('set border 3 back ls 11\n')
    plot.write('set style line 12 lc rgb \'#808080\' lt 0 lw 1\n')
    plot.write('set grid xtics ytics back ls 12\n')
    # Horizontal lines: separate temperature, humidity, and dewpoint
    plot.write('set style line 1 lc rgb \'' + graph_colors[0] + '\' pt 0 ps 1 lt 1 lw 2\n')
    plot.write('set style line 2 lc rgb \'' + graph_colors[1] + '\' pt 0 ps 1 lt 1 lw 2\n')
    plot.write('set style line 3 lc rgb \'' + graph_colors[2] + '\' pt 0 ps 1 lt 1 lw 2\n')
    # Vertical lines: relays 1 - 8
    plot.write('set style line 4 lc rgb \'' + graph_colors[3] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 5 lc rgb \'' + graph_colors[4] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 6 lc rgb \'' + graph_colors[5] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 7 lc rgb \'' + graph_colors[6] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 8 lc rgb \'' + graph_colors[7] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 9 lc rgb \'' + graph_colors[8] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 10 lc rgb \'' + graph_colors[9] + '\' pt 0 ps 1 lt 1 lw 1\n')
    plot.write('set style line 11 lc rgb \'' + graph_colors[10] + '\' pt 0 ps 1 lt 1 lw 1\n')
    # Horizontal lines: combined temperatures and humidities
    plot.write('set style line 12 lc rgb \'' + graph_colors[3] + '\' pt 0 ps 1 lt 1 lw 2\n')
    plot.write('set style line 13 lc rgb \'' + graph_colors[4] + '\' pt 0 ps 1 lt 1 lw 2\n')
    plot.write('set style line 14 lc rgb \'' + graph_colors[5] + '\' pt 0 ps 1 lt 1 lw 2\n')
    plot.write('set style line 15 lc rgb \'' + graph_colors[6] + '\' pt 0 ps 1 lt 1 lw 2\n')
    #plot.write('unset key\n')
    plot.write('set key left top\n')


    #
    # Combined: Generate one large graph combining each condition to its own graph
    #
    if graph_type == "combined" and graph_span != "default":
        multiplot_num = 1
        plot.write('set multiplot layout ' + str(num_graphs) + ',1\n')

        if sum(sensor_t_graph) or sum(sensor_ht_graph) or sum(sensor_press_graph):
            if combined_temp_relays != None:
                y1_min = str(combined_temp_min)
                y1_max = str(combined_temp_max)
                plot.write('set ytics ' + str(combined_temp_tics) + '\n')
                plot.write('set mytics ' + str(combined_temp_mtics) + '\n')
            else:
                y1_min = '0'
                y1_max = '35'
                plot.write('set ytics 5\n')
                plot.write('set mytics 5\n')
            plot.write('set yrange [' + y1_min + ':' + y1_max + ']\n')
            plot.write('set origin 0.0,%.2f\n' % float(1-((1/float(num_graphs))*float(multiplot_num))))
            multiplot_num += 1
            plot.write('set title \"Combined Temperatures: ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot ')
            first = 0;
            line = 0
            for i in range(0, len(sensor_t_name)):
                if sensor_t_graph[i]:
                    if first:
                        plot.write(', ')
                    first = 1
                    plot.write('\"' + sensor_t_log_final[i] + '" u 1:7 index 0 title \"' + sensor_t_name[i] + '\" w lp ls ' + str(line+11) + ' axes x1y1')
                    line += 1
            for i in range(0, len(sensor_ht_name)):
                if sensor_ht_graph[i]:
                    if first:
                        plot.write(', ')
                    first = 1
                    plot.write('\"' + sensor_ht_log_final[i] + '" u 1:7 index 0 title \"' + sensor_ht_name[i] + '\" w lp ls ' + str(line+11) + ' axes x1y1')
                    line += 1
            for i in range(0, len(sensor_press_name)):
                if sensor_press_graph[i]:
                    if first:
                        plot.write(', ')
                    first = 1
                    plot.write('\"' + sensor_press_log_final[i] + '" u 1:7 index 0 title \"' + sensor_press_name[i] + '\" w lp ls ' + str(line+11) + ' axes x1y1')
                    line += 1
            plot.write(' \n')

        if sum(sensor_ht_graph):
            if combined_hum_relays != None:
                y1_min = str(combined_hum_min)
                y1_max = str(combined_hum_max)
                plot.write('set ytics ' + str(combined_hum_tics) + '\n')
                plot.write('set mytics ' + str(combined_hum_mtics) + '\n')
            else:
                y1_max = '100'
                plot.write('set ytics 10\n')
                plot.write('set mytics 5\n')
            plot.write('set yrange [' + y1_min + ':' + y1_max + ']\n')
            plot.write('set origin 0.0,%.2f\n' % float(1-((1/float(num_graphs))*float(multiplot_num))))
            multiplot_num += 1
            plot.write('set title \"Combined Humidities: ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot ')
            first = 0
            for i in range(0, len(sensor_ht_name)):
                if sensor_ht_graph[i]:
                    if first:
                        plot.write(', ')
                    first = 1
                    plot.write('\"' + sensor_ht_log_final[i] + '" u 1:8 index 0 title \"' + sensor_ht_name[i] + '\" w lp ls ' + str(i+11) + ' axes x1y1')
            plot.write(' \n')

        if sum(sensor_co2_graph):
            if combined_co2_relays != None:
                y1_min = str(combined_co2_min)
                y1_max = str(combined_co2_max)
                plot.write('set ytics ' + str(combined_co2_tics) + '\n')
                plot.write('set mytics ' + str(combined_co2_mtics) + '\n')
            else:
                y1_max = '5000'
                plot.write('set ytics 500\n')
            plot.write('unset y2tics\n')
            plot.write('set yrange [' + y1_min + ':' + y1_max + ']\n')
            plot.write('set origin 0.0,%.2f\n' % float(1-((1/float(num_graphs))*float(multiplot_num))))
            multiplot_num += 1
            plot.write('set termopt enhanced\n') 
            plot.write('set title \"Combined CO_2s: ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot ')
            first = 0
            for i in range(0, len(sensor_co2_name)):
                if sensor_co2_graph[i]:
                    if first:
                        plot.write(', ')
                    first = 1
                    plot.write('\"' + sensor_co2_log_final[i] + '" u 1:7 index 0 title \"   ' + sensor_co2_name[i] + '\" w lp ls ' + str(i+11) + ' axes x1y1')
            plot.write(' \n')

        if sum(sensor_press_graph):
            if combined_press_relays != None:
                y1_min = str(combined_press_min)
                y1_max = str(combined_press_max)
                plot.write('set ytics ' + str(combined_press_tics) + '\n')
                plot.write('set mytics ' + str(combined_press_mtics) + '\n')
            else:
                y1_min = '97000'
                y1_max = '99000'
                plot.write('set ytics 200\n')
                plot.write('set mytics 4\n')
            plot.write('set yrange [' + y1_min + ':' + y1_max + ']\n')
            plot.write('\nset origin 0.0,%.2f\n' % float(1-((1/float(num_graphs))*float(multiplot_num))))
            multiplot_num += 1
            plot.write('set title \"Combined Pressures: ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot ')
            first = 0
            for i in range(0, len(sensor_press_name)):
                if sensor_press_graph[i]:
                    if first:
                        plot.write(', ')
                    first = 1
                    plot.write('\"' + sensor_press_log_final[i] + '" u 1:8 index 0 title \"' + sensor_press_name[i] + '\" w lp ls ' + str(i+11) + ' axes x1y1')
            plot.write(' \n')

        plot.write('unset multiplot\n')


    #
    # Separate: Generate a graph for each sensor
    #
    if graph_type == "separate" and graph_span != "default":
        
        if sensor_type == "t":
            if sensor_t_graph_relay:
                plot.write('set multiplot\n')
                plot.write('set size 0.989,0.6\n')
                plot.write('set origin 0.011,0.4\n')
                plot.write('set format x \"\"\n')
                
            plot.write('set yrange [' + str(sensor_t_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_t_yaxis_temp_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_t_yaxis_temp_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_t_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            plot.write('set termopt enhanced\n')
            plot.write('set key at graph 0.02, graph 0.98\n')
            plot.write('set title \"Temp Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_t_name[int(float(sensor_number))] + ' - ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_t_log_final[0] + '\" u 1:7 index 0 title \"T\" w lp ls 1 axes x1y1\n')

            if sensor_t_graph_relay:
                plot.write('set size 1.0,0.4\n')
                plot.write('set origin 0.0,0.0\n')
                plot.write('set key at graph 0.0, graph 0.97\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('unset y2tics\n')
                plot.write('set yrange [' + str(sensor_t_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_t_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_t_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_t_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset title\n')
                plot.write('plot ')

                first = 0
                for i in range(0, len(sensor_t_temp_relays_up_list[int(sensor_number)])):
                    if sensor_t_temp_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_t_temp_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_t_temp_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_t_temp_relays_down_list[int(sensor_number)])):
                    if sensor_t_temp_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_t_temp_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_t_temp_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1

                plot.write(' \n')

        if sensor_type == "ht":
            if sensor_ht_graph_relay:
                plot.write('set multiplot\n')
                plot.write('set size 0.989,0.6\n')
                plot.write('set origin 0.011,0.4\n')
                plot.write('set format x \"\"\n')

            plot.write('set yrange [' + str(sensor_ht_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_temp_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_ht_yaxis_temp_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_ht_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            plot.write('set y2range [' + str(sensor_ht_yaxis_hum_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_hum_max[int(sensor_number)]) + ']\n')
            plot.write('set y2tics ' + str(sensor_ht_yaxis_hum_tics[int(sensor_number)]) + '\n')
            plot.write('set my2tics ' + str(sensor_ht_yaxis_hum_mtics[int(sensor_number)]) + '\n')
            plot.write('set termopt enhanced\n')
            plot.write('set key at graph 0.02, graph 0.98\n')
            plot.write('set title \"Hum/Temp Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_ht_name[int(float(sensor_number))] + ' - ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_ht_log_final[0] + '\" u 1:7 index 0 title \"T\" w lp ls 1 axes x1y1, \\\n')
            plot.write('\"\" u 1:8 index 0 title \"RH\" w lp ls 2 axes x1y2, \\\n')
            plot.write('\"\" u 1:9 index 0 title \"DP\" w lp ls 3 axes x1y1\n')
            
            if sensor_ht_graph_relay:
                plot.write('set size 0.93,0.4\n')
                plot.write('set origin 0.0,0.0\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set key at graph 0.01, graph 0.97\n')
                plot.write('unset y2tics\n')
                plot.write('set yrange [' + str(sensor_ht_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_ht_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_ht_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset title\n')
                plot.write('plot ')
                
                first = 0

                for i in range(0, len(sensor_ht_temp_relays_up_list[int(sensor_number)])):
                    if sensor_ht_temp_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_temp_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_ht_temp_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_ht_temp_relays_down_list[int(sensor_number)])):
                    if sensor_ht_temp_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_temp_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_ht_temp_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_ht_hum_relays_up_list[int(sensor_number)])):
                    if sensor_ht_hum_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_hum_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_ht_hum_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_ht_hum_relays_down_list[int(sensor_number)])):
                    if sensor_ht_hum_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_hum_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_ht_hum_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                
                plot.write('\n')

        if sensor_type == "co2":
            if sensor_co2_graph_relay:
                plot.write('set multiplot\n')
                plot.write('set size 1.0,0.6\n')
                plot.write('set origin 0.0,0.4\n')
                plot.write('set format x \"\"\n')

            plot.write('set yrange [' + str(sensor_co2_yaxis_co2_min[int(sensor_number)]) + ':' + str(sensor_co2_yaxis_co2_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_co2_yaxis_co2_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_co2_yaxis_co2_mtics[int(sensor_number)]) + '\n')
            plot.write('set termopt enhanced\n')
            plot.write('set key at graph 0.035, graph 0.98\n')
            plot.write('set title \"CO_2 Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_co2_name[int(float(sensor_number))] + ' - ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_co2_log_final[0] + '" u 1:7 index 0 title \"CO_2\" w lp ls 1 axes x1y1\n')

            if sensor_co2_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.0\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set key at graph 0.01, graph 0.97\n')
                plot.write('unset y2tics\n')
                plot.write('set yrange [' + str(sensor_co2_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_co2_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_co2_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_co2_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset title\n')
                plot.write('plot ')
                
                first = 0
                for i in range(0, len(sensor_co2_relays_up_list[int(sensor_number)])):
                    if sensor_co2_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_co2_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"  ' + relay_name[sensor_co2_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_co2_relays_down_list[int(sensor_number)])):
                    if sensor_co2_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_co2_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"  ' + relay_name[sensor_co2_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1

                plot.write(' \n')

        if sensor_type == "press":
            if sensor_press_graph_relay:
                plot.write('set multiplot\n')
                plot.write('set size 0.989,0.6\n')
                plot.write('set origin 0.011,0.4\n')
                plot.write('set format x \"\"\n')

            plot.write('set yrange [' + str(sensor_press_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_temp_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_press_yaxis_temp_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_press_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            plot.write('set y2range [' + str(sensor_press_yaxis_press_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_press_max[int(sensor_number)]) + ']\n')
            plot.write('set y2tics ' + str(sensor_press_yaxis_press_tics[int(sensor_number)]) + '\n')
            plot.write('set my2tics ' + str(sensor_press_yaxis_press_mtics[int(sensor_number)]) + '\n')
            plot.write('set termopt enhanced\n')
            plot.write('set key at graph 0.02, graph 0.98\n')
            plot.write('set title \"Press Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_press_name[int(float(sensor_number))] + ' - ' + time_ago + ': ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_press_log_final[0] + '\" u 1:7 index 0 title \"T\" w lp ls 1 axes x1y1, \\\n')
            plot.write('\"\" u 1:8 index 0 title \"Press\" w lp ls 2 axes x1y2\n')
            
            if sensor_press_graph_relay:
                plot.write('set size 0.93,0.4\n')
                plot.write('set origin 0.0,0.0\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set key at graph 0.01, graph 0.97\n')
                plot.write('unset y2tics\n')
                plot.write('set yrange [' + str(sensor_press_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_press_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_press_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset title\n')
                plot.write('plot ')
                
                first = 0
                for i in range(0, len(sensor_press_temp_relays_up_list[int(sensor_number)])):
                    if sensor_press_temp_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_temp_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_press_temp_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_press_temp_relays_down_list[int(sensor_number)])):
                    if sensor_press_temp_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_temp_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_press_temp_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_press_press_relays_up_list[int(sensor_number)])):
                    if sensor_press_press_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_press_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_press_press_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_press_press_relays_down_list[int(sensor_number)])):
                    if sensor_press_press_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_press_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_press_press_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1

                plot.write('\n')


    #
    # Default: Generate a graph of the past day and week periods for each sensor
    #
    if graph_span == "default":

        if sensor_type == "t":
            plot.write('set multiplot\n')
            # Top graph - day
            if sensor_t_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.6\n')
                plot.write('set key at graph 0.025, graph 0.98\n')
                plot.write('set format x ""\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.5\n')
                plot.write('set key at graph 0.025, graph 0.98\n')

            plot.write('set yrange [' + str(sensor_t_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_t_yaxis_temp_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_t_yaxis_temp_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_t_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            plot.write('set title \"Temp Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_t_name[int(float(sensor_number))] + ' - Past Day: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_t_log_final[0] + '" u 1:7 index 0 title \"T\" w lp ls 1 axes x1y1\n')

            if sensor_t_graph_relay:
                plot.write('set size 1.0,0.2\n')
                plot.write('set origin 0.0,0.4\n')
                plot.write('set key at graph 0.015, graph 0.95\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set yrange [' + str(sensor_t_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_t_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_t_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_t_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset title\n')
                plot.write('plot ')

                first = 0
                for i in range(0, len(sensor_t_temp_relays_up_list[int(sensor_number)])):
                    if sensor_t_temp_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_t_temp_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_t_temp_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_t_temp_relays_down_list[int(sensor_number)])):
                    if sensor_t_temp_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_t_temp_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_t_temp_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1

                plot.write(' \n')

            # Bottom graph - week
            d = 7
            time_ago = '1 Week'
            date_ago = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y %m %d %H %M %S")
            date_ago_disp = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y/%m/%d %H:%M:%S")
            if sensor_t_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.0\n')
                plot.write('set yrange [' + str(sensor_t_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_t_yaxis_temp_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_t_yaxis_temp_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_t_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.0\n')

            plot.write('unset xzeroaxis\n')
            plot.write('set title \"Temp Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_t_name[int(float(sensor_number))] + ' - Past Week: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('set format x \"%a\\n%m/%d\"\n')
            plot.write('set xrange [\"' + date_ago + '\":\"' + date_now + '\"]\n')
            plot.write('plot \"' + sensor_t_log_final[1] + '" u 1:7 index 0 notitle w lp ls 1 axes x1y1\n')
            plot.write('unset multiplot\n')


        if sensor_type == "ht":
            plot.write('set multiplot\n')
            # Top graph - day
            if sensor_ht_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.6\n')
                plot.write('set key at graph 0.025, graph 0.98\n')
                plot.write('set format x ""\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.5\n')
                plot.write('set key at graph 0.025, graph 0.98\n')

            plot.write('set yrange [' + str(sensor_ht_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_temp_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_ht_yaxis_temp_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_ht_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            plot.write('set y2range [' + str(sensor_ht_yaxis_hum_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_hum_max[int(sensor_number)]) + ']\n')
            plot.write('set y2tics ' + str(sensor_ht_yaxis_hum_tics[int(sensor_number)]) + '\n')
            plot.write('set my2tics ' + str(sensor_ht_yaxis_hum_mtics[int(sensor_number)]) + '\n')
            plot.write('set title \"Hum/Temp Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_ht_name[int(float(sensor_number))] + ' - Past Day: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_ht_log_final[0] + '" u 1:7 index 0 title \"T\" w lp ls 1 axes x1y1, ')
            plot.write('\"\" u 1:8 index 0 title \"RH\" w lp ls 2 axes x1y2, ')
            plot.write('\"\" u 1:9 index 0 title \"DP\" w lp ls 3 axes x1y1\n')

            if sensor_ht_graph_relay:
                plot.write('set size 0.935,0.2\n')
                plot.write('set origin 0.0,0.4\n')
                plot.write('set key at graph 0.0, graph 0.95\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set yrange [' + str(sensor_ht_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_ht_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_ht_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset y2tics\n')
                plot.write('unset title\n')
                plot.write('plot ')
                
                first = 0

                for i in range(0, len(sensor_ht_temp_relays_up_list[int(sensor_number)])):
                    if sensor_ht_temp_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_temp_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_ht_temp_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_ht_temp_relays_down_list[int(sensor_number)])):
                    if sensor_ht_temp_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_temp_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_ht_temp_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_ht_hum_relays_up_list[int(sensor_number)])):
                    if sensor_ht_hum_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_hum_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_ht_hum_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_ht_hum_relays_down_list[int(sensor_number)])):
                    if sensor_ht_hum_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_ht_hum_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_ht_hum_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                
                plot.write('\n')

            # Bottom graph - week
            d = 7
            time_ago = '1 Week'
            date_ago = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y %m %d %H %M %S")
            date_ago_disp = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y/%m/%d %H:%M:%S")
            if sensor_ht_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.0\n')
                plot.write('set yrange [' + str(sensor_ht_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_temp_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_ht_yaxis_temp_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_ht_yaxis_temp_mtics[int(sensor_number)]) + '\n')
                plot.write('set y2range [' + str(sensor_ht_yaxis_hum_min[int(sensor_number)]) + ':' + str(sensor_ht_yaxis_hum_max[int(sensor_number)]) + ']\n')
                plot.write('set y2tics ' + str(sensor_ht_yaxis_hum_tics[int(sensor_number)]) + '\n')
                plot.write('set my2tics ' + str(sensor_ht_yaxis_hum_mtics[int(sensor_number)]) + '\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.0\n')

            plot.write('unset xzeroaxis\n')
            plot.write('set title \"Hum/Temp Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_ht_name[int(float(sensor_number))] + ' - Past Week: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('set format x \"%a\\n%m/%d\"\n')
            plot.write('set xrange [\"' + date_ago + '\":\"' + date_now + '\"]\n')
            plot.write('plot \"' + sensor_ht_log_final[1] + '" u 1:7 index 0 notitle w lp ls 1 axes x1y1, ')
            plot.write('\"\" u 1:8 index 0 notitle w lp ls 2 axes x1y2, ')
            plot.write('\"\" u 1:9 index 0 notitle w lp ls 3 axes x1y1\n')
            plot.write('unset multiplot\n')


        if sensor_type == "co2":
            plot.write('set multiplot\n')
            # Top graph - day
            if sensor_co2_graph_relay:
                plot.write('set size 1.0,0.4\n')
                plot.write('set origin 0.0,0.6\n')
                plot.write('set key at graph 0.035, graph 0.98\n')
                plot.write('set format x ""\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.5\n')
                plot.write('set key at graph 0.035, graph 0.98\n')

            plot.write('set yrange [' + str(sensor_co2_yaxis_co2_min[int(sensor_number)]) + ':' + str(sensor_co2_yaxis_co2_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_co2_yaxis_co2_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_co2_yaxis_co2_mtics[int(sensor_number)]) + '\n')
            plot.write('set termopt enhanced\n')
            plot.write('set title \"CO_2 Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_co2_name[int(float(sensor_number))] + ' - Past Day: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_co2_log_final[0] + '" u 1:7 index 0 title \"CO_2\" w lp ls 1 axes x1y1\n')

            if sensor_co2_graph_relay:
                plot.write('set size 0.989,0.2\n')
                plot.write('set origin 0.011,0.4\n')
                plot.write('set key at graph 0.01, graph 0.95\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set yrange [' + str(sensor_co2_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_co2_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_co2_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_co2_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset title\n')
                plot.write('plot ')
                
                first = 0
                for i in range(0, len(sensor_co2_relays_up_list[int(sensor_number)])):
                    if sensor_co2_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_co2_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"  ' + relay_name[sensor_co2_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_co2_relays_down_list[int(sensor_number)])):
                    if sensor_co2_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_co2_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"  ' + relay_name[sensor_co2_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1

                plot.write(' \n')

            # Bottom graph - week
            d = 7
            time_ago = '1 Week'
            date_ago = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y %m %d %H %M %S")
            date_ago_disp = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y/%m/%d %H:%M:%S")
            if sensor_co2_graph_relay:
                plot.write('set size 1.0,0.4\n')
                plot.write('set origin 0.0,0.0\n')
                plot.write('set yrange [' + str(sensor_co2_yaxis_co2_min[int(sensor_number)]) + ':' + str(sensor_co2_yaxis_co2_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_co2_yaxis_co2_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_co2_yaxis_co2_mtics[int(sensor_number)]) + '\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.0\n')

            plot.write('unset xzeroaxis\n')
            plot.write('set title \"CO_2 Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_co2_name[int(float(sensor_number))] + ' - Past Week: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('set format x \"%a\\n%m/%d\"\n')
            plot.write('set xrange [\"' + date_ago + '\":\"' + date_now + '\"]\n')
            plot.write('plot \"' + sensor_co2_log_final[1] + '" u 1:7 index 0 notitle w lp ls 1 axes x1y1\n')
            plot.write('unset multiplot\n')

        if sensor_type == "press":
            plot.write('set multiplot\n')
            # Top graph - day
            if sensor_press_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.6\n')
                plot.write('set key at graph 0.025, graph 0.98\n')
                plot.write('set format x ""\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.5\n')
                plot.write('set key at graph 0.025, graph 0.98\n')

            plot.write('set yrange [' + str(sensor_press_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_temp_max[int(sensor_number)]) + ']\n')
            plot.write('set ytics ' + str(sensor_press_yaxis_temp_tics[int(sensor_number)]) + '\n')
            plot.write('set mytics ' + str(sensor_press_yaxis_temp_mtics[int(sensor_number)]) + '\n')
            plot.write('set y2range [' + str(sensor_press_yaxis_press_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_press_max[int(sensor_number)]) + ']\n')
            plot.write('set y2tics ' + str(sensor_press_yaxis_press_tics[int(sensor_number)]) + '\n')
            plot.write('set my2tics ' + str(sensor_press_yaxis_press_mtics[int(sensor_number)]) + '\n')
            plot.write('set title \"Pressure Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_press_name[int(float(sensor_number))] + ' - Past Day: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('plot \"' + sensor_press_log_final[0] + '" u 1:7 index 0 title \"T\" w lp ls 1 axes x1y1, ')
            plot.write('\"\" u 1:8 index 0 title \"Press\" w lp ls 2 axes x1y2\n')

            if sensor_press_graph_relay:
                plot.write('set size 0.935,0.2\n')
                plot.write('set origin 0.0,0.4\n')
                plot.write('set key at graph 0.0, graph 0.95\n')
                plot.write('set format x \"%H:%M\\n%m/%d\"\n')
                plot.write('set yrange [' + str(sensor_press_yaxis_relay_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_relay_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_press_yaxis_relay_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_press_yaxis_relay_mtics[int(sensor_number)]) + '\n')
                plot.write('set xzeroaxis linetype 1 linecolor rgb \'#000000\' linewidth 1\n')
                plot.write('unset y2tics\n')
                plot.write('unset title\n')
                plot.write('plot ')
                
                first = 0
                for i in range(0, len(sensor_press_temp_relays_up_list[int(sensor_number)])):
                    if sensor_press_temp_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_temp_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_press_temp_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_press_temp_relays_down_list[int(sensor_number)])):
                    if sensor_press_temp_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_temp_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_press_temp_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_press_press_relays_up_list[int(sensor_number)])):
                    if sensor_press_press_relays_up_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_press_relays_up_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(abs($10)) index 0 title \"' + relay_name[sensor_press_press_relays_up_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1
                for i in range(0, len(sensor_press_press_relays_down_list[int(sensor_number)])):
                    if sensor_press_press_relays_down_list[int(sensor_number)][i] != 0:
                        if first:
                            plot.write(', \\\n')
                        plot.write('\"<awk \'$8 == ' + str(sensor_press_press_relays_down_list[int(sensor_number)][i]) + '\' ' + relay_log_generate + '"')
                        plot.write(' u 1:(-abs($10)) index 0 title \"' + relay_name[sensor_press_press_relays_down_list[int(sensor_number)][i]-1] + '\" w impulses ls ' + str(first+4) + ' axes x1y1')
                        first += 1

                plot.write('\n')

            # Bottom graph - week
            d = 7
            time_ago = '1 Week'
            date_ago = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y %m %d %H %M %S")
            date_ago_disp = (datetime.datetime.now() - datetime.timedelta(hours=h, days=d)).strftime("%Y/%m/%d %H:%M:%S")
            if sensor_press_graph_relay:
                plot.write('set size 0.989,0.4\n')
                plot.write('set origin 0.011,0.0\n')
                plot.write('set yrange [' + str(sensor_press_yaxis_temp_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_temp_max[int(sensor_number)]) + ']\n')
                plot.write('set ytics ' + str(sensor_press_yaxis_temp_tics[int(sensor_number)]) + '\n')
                plot.write('set mytics ' + str(sensor_press_yaxis_temp_mtics[int(sensor_number)]) + '\n')
                plot.write('set y2range [' + str(sensor_press_yaxis_press_min[int(sensor_number)]) + ':' + str(sensor_press_yaxis_press_max[int(sensor_number)]) + ']\n')
                plot.write('set y2tics ' + str(sensor_press_yaxis_press_tics[int(sensor_number)]) + '\n')
                plot.write('set my2tics ' + str(sensor_press_yaxis_press_mtics[int(sensor_number)]) + '\n')
            else:
                plot.write('set size 1.0,0.5\n')
                plot.write('set origin 0.0,0.0\n')

            plot.write('unset xzeroaxis\n')
            plot.write('set title \"Press Sensor ' + str(int(sensor_number)+1) + ': ' + sensor_press_name[int(float(sensor_number))] + ' - Past Week: ' + date_ago_disp + ' - ' + date_now_disp + '\"\n')
            plot.write('set format x \"%a\\n%m/%d\"\n')
            plot.write('set xrange [\"' + date_ago + '\":\"' + date_now + '\"]\n')
            plot.write('plot \"' + sensor_press_log_final[1] + '" u 1:7 index 0 notitle w lp ls 1 axes x1y1, ')
            plot.write('\"\" u 1:8 index 0 notitle w lp ls 2 axes x1y2\n')
            plot.write('unset multiplot\n')

    plot.close()

    # Generate graph with gnuplot with the above generated command sequence
    if logging.getLogger().isEnabledFor(logging.DEBUG) == False:
        subprocess.call(['gnuplot', gnuplot_graph])

        # Delete all temporary files
        os.remove(gnuplot_graph)
        os.remove(relay_log_generate)

        if graph_span == "default":
            if sensor_type == "t":
                os.remove(sensor_t_log_generate)
                os.remove(sensor_t_log_final[0])
                os.remove(sensor_t_log_final[1])
            if sensor_type == "ht":
                os.remove(sensor_ht_log_generate)
                os.remove(sensor_ht_log_final[0])
                os.remove(sensor_ht_log_final[1])
            if sensor_type == "co2":
                os.remove(sensor_co2_log_generate)
                os.remove(sensor_co2_log_final[0])
                os.remove(sensor_co2_log_final[1])
            if sensor_type == "press":
                os.remove(sensor_press_log_generate)
                os.remove(sensor_press_log_final[0])
                os.remove(sensor_press_log_final[1])
        elif graph_type == "combined":
            if sum(sensor_t_graph):
                os.remove(sensor_t_log_generate)
            if sum(sensor_ht_graph):
                os.remove(sensor_ht_log_generate)
            if sum(sensor_co2_graph):
                os.remove(sensor_co2_log_generate)
            if sum(sensor_press_graph):
                os.remove(sensor_press_log_generate)
            for i in range(0, len(sensor_t_name)):
                if sensor_t_graph[i]:
                    os.remove(sensor_t_log_final[i])
            for i in range(0, len(sensor_ht_name)):
                if sensor_ht_graph[i]:
                    os.remove(sensor_ht_log_final[i])
            for i in range(0, len(sensor_co2_name)):
                if sensor_co2_graph[i]:
                    os.remove(sensor_co2_log_final[i])
            for i in range(0, len(sensor_press_name)):
                if sensor_press_graph[i]:
                    os.remove(sensor_press_log_final[i])
        elif graph_type == "separate":
            if sensor_type == "t":
                os.remove(sensor_t_log_generate)
                os.remove(sensor_t_log_final[0])
            if sensor_type == "ht":
                os.remove(sensor_ht_log_generate)
                os.remove(sensor_ht_log_final[0])
            if sensor_type == "co2":
                os.remove(sensor_co2_log_generate)
                os.remove(sensor_co2_log_final[0])
            if sensor_type == "press":
                os.remove(sensor_press_log_generate)
                os.remove(sensor_press_log_final[0])
    else:
        gnuplot_log = "%s/plot-%s-%s-%s-%s.log" % (log_path, sensor_type, graph_type, graph_span, sensor_number)
        with open(gnuplot_log, 'ab') as errfile:
            subprocess.call(['gnuplot', gnuplot_graph], stderr=errfile)

    logging.debug("[Generate Graph] Finished")