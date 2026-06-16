#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

# intfsum - Fetch interface summary

require "./jsonlib.pl";
use IOG::SKVS;

my %RESPONSE = (
    error => 0
);


if ( 1 == IOG::SKVS::get("FC_ETH_SWITCH") ) {
    $RESPONSE{summary} = `/bin/snswrpt -e 0`;
    if ( 1 == IOG::SKVS::get("FC_SWMODE_SEP") ) {
        $RESPONSE{summary} .= `/bin/snswrpt -e 1`;
    }
    $RESPONSE{summary} .= "\n\n" . `/bin/snswrpt | /bin/sed 's/\\/bin\\///'`;
}
else {
    if (`/sbin/ifconfig` =~ /eth1/) {
        $RESPONSE{summary} = `/sbin/ethtool eth0; /sbin/ethtool eth1`;
    }
    else {
        $RESPONSE{summary} = `/sbin/ethtool eth0`;
    }
}
$RESPONSE{details} = `/sbin/ip addr show`;
$RESPONSE{multicast} = `/sbin/ip maddr show`;

print "Content-type: text/html; charset=utf8\n\n";
print &JSON_Serialize(\%RESPONSE);
