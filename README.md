# WEB MONITORING CLI
![App Visual](misc/visual.png?raw=true)

## Installation 

To install the app simply clone the project, and you are good to go! Don't worry it is light ヽ(´▽`)/

_NOTE : The app requires the user to have installed python 3 !_

## Starting the app - Commands

to start the app type go to your _webMonitoring-CLI_ directory and type ```python3 main.py {cmd}```

with one of the following command : 

    * -h to open help
    * user {username} to access the user interface for the specified user
    * monitor {username} to access the monitoring interface for the specified user

## Mailing Alert 

If you want to be notified by mail whenever an alert is triggered (Website up or down basically), you can add your email address 
in the field _mailrecipient_ (line 4) of the _mailSender_ file

## MultiProcessing

The following diagram describes how are organized the different processes used in the app
![Multi Processing Schema](misc/processesWCLI.png?raw=true)



# ENHANCEMENTS

You can see my proposition for enhancements here : [Enhancement File](misc/ENHANCEMENTS.md)

# ISSUES 

install certification command for ssl in mac 

contains the shell script : 
```#!/bin/sh
   
   /Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6 << "EOF"
   
   # install_certifi.py
   #
   # sample script to install or update a set of default Root Certificates
   # for the ssl module.  Uses the certificates provided by the certifi package:
   #       https://pypi.python.org/pypi/certifi
   
   import os
   import os.path
   import ssl
   import stat
   import subprocess
   import sys
   
   STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
                | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
                | stat.S_IROTH |                stat.S_IXOTH )
   
   def main():
       openssl_dir, openssl_cafile = os.path.split(
           ssl.get_default_verify_paths().openssl_cafile)
   
       print(" -- pip install --upgrade certifi")
       subprocess.check_call([sys.executable,
           "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])
   
       import certifi
   
       # change working directory to the default SSL directory
       os.chdir(openssl_dir)
       relpath_to_certifi_cafile = os.path.relpath(certifi.where())
       print(" -- removing any existing file or link")
       try:
           os.remove(openssl_cafile)
       except FileNotFoundError:
           pass
       print(" -- creating symlink to certifi certificate bundle")
       os.symlink(relpath_to_certifi_cafile, openssl_cafile)
       print(" -- setting permissions")
       os.chmod(openssl_cafile, STAT_0o775)
       print(" -- update complete")
   
   if __name__ == '__main__':
       main()
   EOF
```

