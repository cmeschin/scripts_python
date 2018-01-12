#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Launch the supervisorctl for view status process
"""

import os, subprocess

cmd = "sudo supervisorctl status"
path = "/supervision/resultats/"
supervisorctl = "status_process_supervisorctl.txt"
status_supervisorctl = (path + supervisorctl)

#List the file in directory for delete file_status
for root, dirs, files in os.walk(path):
    for filename in files:
        print(filename)

os.remove(status_supervisorctl)

#Launch the new file_status
subprocess.run(cmd= $cmd, output= $path_$status_supervisorctl)