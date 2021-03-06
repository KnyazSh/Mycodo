# Mycodo

   Mycodo is a system designed to monitor an environment and regulate the climate with discrete PID control. Sensors monitor environmental conditions (currently temperature, humidity, CO<sub>2</sub>, and barometric pressure) and software PID controllers modulate relays that power devices to alter the environment. A web-interface features viewing of current and past conditions as well as graph generation, configuration modification, and image/video/timelapse acquisition, to name a few (full feature list below).

   A daemon performs all crucial tasks, including periodically reading sensors, writing sensor and relay logs, PID controller regulation, scheduling timer-activated relays, generating graphs, among others. A client application communicates with the daemon to carry out user-defined tasks, such as relay changes and turning PID regulation on and off, to name a few.

   The web interface allows the user to interact with the daemon to perform tasks such as configure sensors/relays/PID controllers, view sensor data, generate and view graphs, and manage users.

## Index

+ [History](#history)
+ [Features](#feat)
+ [Hardware Brief](#hard-brief)
+ [Software Brief](#soft-brief)
+ [License](#license)
+ [Useful Links](#links)

<a name="history"></a>
## History

Mycodo started as a small project desgined to regulate the temperature and humidity of a growth chamber used for cultivating gourmet mushrooms. It has since developed into a feature-rich system that has been used by mushroom-growers as well as for other purposes, including growing plants and aging cheeses.

With its inception in 2010, the first system was comprised of an ATMega interfaced to a network-connected computer running linux. My first relay bank consisted of 4 relays, controlling a heater, humidifier, circulatory fan, and HEPA-filtered exhaust fan. When the Raspberry Pi was introduced in 2012, I decided to port the code from the ATMega and my linux computer to the Pi. I've since upgraded to a new set of hardware that support 8 individually-switchable 120-volt AC outlets, however the latest software (v3.5) aims to support as many sensors and relays as can be connected. Additionally, the current software skeleton supports the ability to efficiently add support for new sensors. If you have a sensor you would like to see incorporated, let me know and you can become a beta-tester for a new sensor.

<a name="feat"></a>
## Features

### Revisions at a Glance

<table>
    <tr>
        <td>
            Mycodo Version
        </td>
        <td>
            v1.0
        </td>
        <td>
            v2.0
        </td>
        <td>
            v3.0
        </td>
        <td>
            v3.5
        </td>
    </tr>
    <tr>
        <td>
            Platform
        </td>
        <td>
            ATMega
        </td>
        <td>
            Raspberry Pi
        </td>
        <td>
            Raspberry Pi
        </td>
        <td>
            Raspberry Pi
        </td>
    </tr>
    <tr>
        <td>
            Controller Regulation
        </td>
        <td>
            P
        </td>
        <td>
            P
        </td>
        <td>
            PID (Up only)
        </td>
        <td>
            PID (Up and Down)
        </td>
    </tr>
    <tr>
        <td>
            Supported Sensors
        </td>
        <td>
            1
        </td>
        <td>
            1
        </td>
        <td>
            3
        </td>
        <td>
            7
        </td>
    </tr>
    <tr>
        <td>
            Measurments
        </td>
        <td>
            Temperature, Humidity
        </td>
        <td>
            Temperature, Humidity
        </td>
        <td>
            Temperature, Humidity
        </td>
        <td>
            Temperature, Humidity, CO<sub>2</sub>, Barometric Pressure
        </td>
    </tr>
    <tr>
        <td>
            Number of Sensors
        </td>
        <td>
            1
        </td>
        <td>
            1
        </td>
        <td>
            4
        </td>
        <td>
            Unlimited
        </td>
    </tr>
    <tr>
        <td>
            Number of Relays
        </td>
        <td>
            4
        </td>
        <td>
            4
        </td>
        <td>
            8
        </td>
        <td>
            Unlimited
        </td>
    </tr>
    <tr>
        <td>
            Camera Support
        </td>
        <td>
            None
        </td>
        <td>
            None
        </td>
        <td>
            Still Image
        </td>
        <td>
            Still, Video, Time-lapse
        </td>
    </tr>
    <tr>
        <td>
            Configuration Database
        </td>
        <td>
            Plain-text
        </td>
        <td>
            Plain-text
        </td>
        <td>
            Plain-text
        </td>
        <td>
            SQLite
        </td>
    </tr>
    <tr>
        <td>
            User Database
        </td>
        <td>
            None
        </td>
        <td>
            None
        </td>
        <td>
            MySQL
        </td>
        <td>
            SQLite
        </td>
    </tr>
</table>

### Full List of Features

#### v1.0

* Read humidity & temperature sensor with an ATMega
* ATMega connected by serial USB to a network-enabled computer running linux
* Linux periodically reads humidity/temperature sensor and writes log
* ATMega modulates relays for simple proportional humidity/temperature regulation
* Simple web interface to view historical data and generate graphs with gnuplot

#### v2.0

* All software running on a Raspberry Pi version 1 Model B
* Support for the DHT22 digital humidity and temperature sensor
* Manual or automatic switching of up to four 120-volt AC relays
* Automatic operation by simple proportional temperature/humidity regulation
* Temperature, humidity, and relay state-change logging
* Basic web interface
  * Configure variables related to sensor reading, log writing, and graph generation
  * Generate custom graphs of current and past data
    * Presets of pre-defined time periods (past 1 hour, 6 hours, 1 day, 3 days...)
    * Specify specific time period to generate graph

#### v3.0-stable

* Upgrade to eight 120-volt AC relays
* Support for up to 8 simple timers (define on duration, off duration)
* True PID control for temperature and humidity regulation
* Support more humidity & temperature sensors (DHT11, DHT22, and AM2302)
* Multi-sensors support to regulate multiple environments
* TempFS to reduce writes and extend the life of the SD card
* Lock files to prevent sensor read and file access conflicts
* New logs to view: login authorization, daemon, sensor, and relay logs
* Generate new types of graphs
  * Combined: generate a graph combining the same sensor readings (temperatures, humidities)
  * Separate: generate a graph of the measurements of each sensor
  * Define graph image width (custom graph only)
* Acquire still image or stream live video using the Raspberry Pi camera module
  * Set relay (light) to be turned on while camera is capturing
* New web interface
  * Tabs allow everything to be loaded on one page
  * Easy change any variable in the configuration file
  * Login authentication (by php-login.net)
    * Optional cookie to keep session authenticated
    * Guest account for viewing only (no config changes permitted) (user: guest, password: anonymous)
    * Authorization log of successful and unsuccessful login attempts
    * User profile, gravatar support (from email), lost/forgot email password reset

#### v3.5-beta (experimental)

This is an experimental branch of mycodo. This will be a future stable release once a certain number of features have been added and when it's relatively bug-free. Unless I have been in direct contact with you regarding testing of this branch, I will not be providing technical support for any issues with this version. Instead, I recommend you check out the v3.0 stable branch.

See [/3.5/README.md](3.5/README.md) for progress updates

<a name="hard-brief"></a>
## Hardware

* Raspberry Pi
* Sensors
* Relays
* Environmental manipulating devices (humidifier, heater, circulatory fan, exhaust fan, etc)

<a name="soft-brief"></a>
## Software

The following software is required for version 3.0 (stable)

* apache2
* git
* gnuplot
* mysql
* php >= 5.3.7
* phpmyadmin (optional but recommended)
* python and modules
  * Adafruit_Python_DHT
  * LockFile
  * WiringPi
* subversion
* wget

Note: version 3.5 replaces mysql with sqlite

<a name="license"></a>
## License

Mycodo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Mycodo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU General Public License](http://www.gnu.org/licenses/gpl-3.0.en.html) for more details.

A full copy of the GNU General Public License can be found at <a href="http://www.gnu.org/licenses/gpl-3.0.en.html" target="_blank">http://www.gnu.org/licenses/gpl-3.0.en.html</a>

This software includes third party open source software components: Discrete PID Controller. Each of these software components have their own license. Please see ./3.5/cgi-bin/mycodoPID.py for license information.

<a name="links"></a>
## Useful Links

Thanks for using and supporting my software, however it may not be the latest version or it may have been altered if not obtained through an official distribution site. You should be able to find the latest version on github or my web site.

https://github.com/kizniche/Mycodo

http://KyleGabriel.com