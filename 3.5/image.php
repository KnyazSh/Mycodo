<?php
/*
*  image.php - Authenticates the tranfer of files, images, and video
*              streams from protected locations.
*
*  Copyright (C) 2015  Kyle T. Gabriel
*
*  This file is part of Mycodo
*
*  Mycodo is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  Mycodo is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with Mycodo. If not, see <http://www.gnu.org/licenses/>.
*
*  Contact at kylegabriel.com
*/

####### Configure #######
$install_path = "/var/www/mycodo";

$image_dir = $install_path . "/images/";
$still_dir = $install_path . "/camera-stills/";
$timelapse_dir = $install_path . "/camera-timelapse/";
$upload_dir = $install_path . "/notes/uploads/";
$hdr_dir = $install_path . "/camera-hdr/";
$mycodo_client = $install_path . "/cgi-bin/mycodo-client.py";

require_once("includes/auth.php"); // Check authorization to view

if ($_COOKIE['login_hash'] == $user_hash) {
    if (isset($_GET['graphtype']) && ($_GET['graphtype'] == 'custom-separate' || $_GET['graphtype'] == 'custom-combined')) {
        header('Content-Type: image/png');
        // Generate custom graph (Graph tab)
        if (isset($_GET['sensortype'])) {
            readfile($image_dir . 'graph-' . $_GET['sensortype'] . "-" . $_GET['graphtype'] . '-' . $_GET['id'] . '-' . $_GET['sensornumber'] . '.png');
        } else {
            readfile($image_dir . 'graph-' . $_GET['graphtype'] . '-' . $_GET['id'] . '-' . $_GET['sensornumber'] . '.png');
        }
    } else if (isset($_GET['span'])) {
        // Display still image from RPi camera (Camera tab)
        switch ($_GET['span']) {
            case 'cam-still':
                header('Content-Type: image/png');
                $files = scandir($still_dir, SCANDIR_SORT_DESCENDING);
                $newest_file = $files[0];
                readfile($still_dir . $newest_file);
                break;
            case 'cam-timelapse':
                header('Content-Type: image/png');
                $files = scandir($timelapse_dir, SCANDIR_SORT_DESCENDING);
                $newest_file = $files[0];
                readfile($timelapse_dir . $newest_file);
                break;
            case 'cam-hdr':
                header('Content-Type: image/png');
                $files = scandir($still_dir, SCANDIR_SORT_DESCENDING);
                $newest_file = $files[0];
                readfile($still_dir . $newest_file);
                break;
            case 'stream':
                if ($_COOKIE['login_hash'] == $user_hash) {
                    $server = "localhost"; // camera server address
                    $port = 6926; // camera server port
                    $url = "/?action=stream"; // image url on server
                    set_time_limit(0);  
                    $fp = fsockopen($server, $port, $errno, $errstr, 30); 
                    if (!$fp) { 
                            echo "$errstr ($errno)<br>\n";   // error handling
                    } else {
                            $urlstring = "GET ".$url." HTTP/1.0\r\n\r\n"; 
                            fputs ($fp, $urlstring); 
                            while ($str = trim(fgets($fp, 4096))) 
                            header($str); 
                            fpassthru($fp); 
                            fclose($fp); 
                    }
                }
                break;
            case 'ul-png':
                header('Content-Type: image/png');
                readfile($upload_dir . $_GET['file']);
                break;
            case 'ul-jpg':
                header('Content-Type: image/jpeg');
                readfile($upload_dir . $_GET['file']);
                break;
            case 'ul-gif':
                header('Content-Type: image/gif');
                readfile($upload_dir . $_GET['file']);
                break;
            case 'ul-dl':
                $quoted = sprintf('"%s"', addcslashes(basename($upload_dir . $_GET['file']), '"\\'));
                $size   = filesize($upload_dir . $_GET['file']);
                header('Content-Description: File Transfer');
                header('Content-Type: application/octet-stream');
                header('Content-Disposition: attachment; filename=' . $quoted); 
                header('Content-Transfer-Encoding: binary');
                header('Connection: Keep-Alive');
                header('Expires: 0');
                header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
                header('Pragma: public');
                header('Content-Length: ' . $size);
                readfile($upload_dir . $_GET['file']);
                break;
            }
    } else if (ctype_alnum($_GET['id']) && is_int((int)$_GET['sensornumber']) &&
            ($_GET['sensortype'] == 't' || $_GET['sensortype'] == 'ht' || $_GET['sensortype'] == 'co2' || $_GET['sensortype'] == 'press' || $_GET['sensortype'] == 'x')) {
        header('Content-Type: image/png');
        // Generate preset graphs (Main tab)
        if ($_GET['graphtype'] == 'separate' ||
            $_GET['graphtype'] == 'combined' ||
            $_GET['graphspan'] == 'default') {
            readfile($image_dir . 'graph-' . $_GET['sensortype'] . $_GET['graphtype'] . $_GET['graphspan'] . '-' . $_GET['id'] . '-' . $_GET['sensornumber'] . '.png');
        } elseif ($_GET['graphtype'] == 'combinedcustom') {
            readfile($image_dir . 'graph-' . $_GET['sensortype'] . $_GET['graphtype'] . '-' . $_GET['id'] . '-custom.png');
        } elseif ($_GET['graphtype'] == 'separatecustom') {
            readfile($image_dir . 'graph-' . $_GET['sensortype'] . $_GET['graphtype'] . '-' . $_GET['id'] . '-' . $_GET['sensornumber'] . '.png');
        } elseif ($_GET['graphtype'] == 'legend-small') {
            $id = uniqid();
            shell_exec($mycodo_client . ' --graph mone legend-small none' . $id . ' 0');
            readfile($image_dir . 'graph-' . $_GET['graphtype'] . '-' . $id . '.png');
        } elseif ($_GET['graphtype'] == 'legend-full') {
            $id = uniqid();
            shell_exec($mycodo_client . ' --graph none legend-full none' . $id . ' 0');
            readfile($image_dir . 'graph-' . $_GET['graphtype'] . '-' . $id . '.png');
        } 
    }
}
?>  