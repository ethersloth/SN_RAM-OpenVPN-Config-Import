#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Building all the Object Mapping I/O types to be appended 
# to /etc/stacfg/sxdnpdrv.ini DNP3 driver configuration file.

/home/httpd/jbmconfig/bin/binaryinput
logger "Building /etc/stacfg/sxbinaryinput file."

/home/httpd/jbmconfig/bin/analoginput                                                           
logger "Building /etc/stacfg/sxanaloginput file."                                                          

/home/httpd/jbmconfig/bin/floatinput                                                           
logger "Building /etc/stacfg/sxfloatinput file."                                                          

/home/httpd/jbmconfig/bin/longinput                                                           
logger "Building /etc/stacfg/sxlonginput file."                                                          


/home/httpd/jbmconfig/bin/binarycounter                                                           
logger "Building /etc/stacfg/sxbinarycounter file."                                                          

exit
