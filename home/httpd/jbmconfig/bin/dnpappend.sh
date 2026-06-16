#!/bin/bash
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Appending all the Object Mapping I/O types DNP Points                                                      
# to /etc/stacfg/sxdnpdrv.ini DNP3 driver configuration file.

cat /etc/stacfg/sxbinaryinput >> /etc/stacfg/sxdnpdrv.ini
logger "Appending /etc/stacfg/sxbinaryinput to /etc/stacfg/sxdnpdrv.ini DNP3 configuration file."

cat /etc/stacfg/sxanaloginput >> /etc/stacfg/sxdnpdrv.ini     
logger "Appending /etc/stacfg/sxanaloginput to /etc/stacfg/sxdnpdrv.ini DNP3 configuration file."                                    

cat /etc/stacfg/sxfloatinput >> /etc/stacfg/sxdnpdrv.ini     
logger "Appending /etc/stacfg/sxfloatinput to /etc/stacfg/sxdnpdrv.ini DNP3 configuration file."                                    

cat /etc/stacfg/sxlonginput >> /etc/stacfg/sxdnpdrv.ini     
logger "Appending /etc/stacfg/sxlonginput to /etc/stacfg/sxdnpdrv.ini DNP3 configuration file."                                    

cat /etc/stacfg/sxbinarycounter >> /etc/stacfg/sxdnpdrv.ini     
logger "Appending /etc/stacfg/sxbinarycounter to /etc/stacfg/sxdnpdrv.ini DNP3 configuration file."                                    

exit
