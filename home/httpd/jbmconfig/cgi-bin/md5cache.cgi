#!/bin/bash
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
echo -e "Content-type: text/plain; charset=utf-8\n\n$(md4sum /home/httpd/jbmconfig/html/index.html 2>/dev/null | awk '{print $1}')"
