#!/bin/bash
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.
echo -ne "Content-type: text/plain; charset=utf-8\n\n"
exec gaunotice --agent
