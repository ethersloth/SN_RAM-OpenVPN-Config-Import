#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

use strict;
use warnings;

use IOG::CGI;
require "./cgi-lib.pl";

my %RESPONSE = (
	error => 0
);

$ENV{PATH} .= ":/bin:/sbin:/usr/bin:/home/httpd/jbmconfig/bin";

my $openvpn_parse_cfg_name = "/etc/openvpn/openvpn_cfg_parse.cfg";
my %sub_systems = ('default'       => {fetch   => '/home/httpd/jbmconfig/txt/expert.txt',
                                       default => '/home/httpd/jbmconfig/txt/expert.txt',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'custom_tabs'   => {fetch   => '/home/httpd/jbmconfig/txt/customTabs.txt',
                                       default => '/home/httpd/jbmconfig/txt/customTabs.txt.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
               'custom_function'   => {fetch   => '/etc/common/custom/custom_function.sh',
                                       default => '/etc/common/custom/custom_function.orig',
                                       stop    => 'chmod -x /etc/common/custom/custom_function.sh',
                                       start   => 'chmod +x /etc/common/custom/custom_function.sh',
                                       save    => 1},
                   'dhcpd'         => {fetch   => '/etc/dhcpd/dhcpd.conf',
                                       default => '/etc/dhcpd/dhcpd.conf.sample',
                                       stop    => 'chkconfig dhcpd off;service dhcpd stop',
                                       start   => 'chkconfig dhcpd on;service dhcpd restart',
                                       save    => 1},
            'dhcprelay_strongsec'  => {fetch   => '/etc/dhcrelay/dhcrelay_strongsec.conf',
                                       default => '/etc/dhcrelay/dhcrelay_strongsec.conf.orig',
                                       stop    => 'chkconfig dhcrelay_strongsec off;service dhcrelay_strongsec stop',
                                       start   => 'chkconfig dhcrelay_strongsec on;service dhcrelay_strongsec restart',
                                       save    => 1},
                   'dhcprelay'    => {fetch   => '/etc/dhcrelay/dhcrelay.conf',
                                       default => '/etc/dhcrelay/dhcrelay.conf.orig',
                                       stop    => 'chkconfig dhcrelay off;service dhcrelay stop',
                                       start   => 'chkconfig dhcrelay on;service dhcrelay restart',
                                       save    => 1},
                   'gpscontrol'     => {fetch   => '/etc/jbm/gps/gpsc.conf',
                                       default => '/etc/jbm/gps/gpsc.conf.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'gpsmode'       => {fetch   => '/etc/jbm/wireless/cellmodem_gpstypepref',
                                       default => '/etc/jbm/wireless/cellmodem_gpstypepref.orig',
                                       stop    => '',
                                       start   => '',
                                        save   => 1},
                   'igmpproxy'     => {fetch   => '/etc/igmpproxy/igmpproxy.conf',
                                       default => '/etc/igmpproxy/igmpproxy.conf.orig',
                                       stop    => 'chkconfig igmpproxy off;service igmpproxy stop',
                                       start   => 'chkconfig igmpproxy on;service igmpproxy restart',
                                       save    => 1},
                   'iocontrol'     => {fetch   => '/etc/ioctrl/io.conf',
                                       default => '/etc/ioctrl/io.conf.orig',
                                       stop    => 'chkconfig iocontrol off;service iocontrol stop',
                                       start   => 'chkconfig iocontrol on;service iocontrol restart',
                                       save    => 1},
                   'wireless_provision' => {fetch   => '/etc/jbm/wireless/cellmodem_provision_data.conf',
                                       default => '/etc/jbm/wireless/cellmodem_provision_data.conf.orig',
                                       stop    => '',
                                       start   => '',
                                        save    => 1},
                   'jbmoob'        => {fetch   => '/etc/jbm/jbm_oob.conf',
                                       default => '/etc/jbm/jbm_oob.conf.orig',
                                       stop    => 'jbm_oob disable',
                                       start   => 'jbm_oob enable',
                                       save    => 1},
                   'lighttpdconf'  => {fetch   => '/etc/lighttpd/lighttpd.conf',
                                       default => '/etc/lighttpd/lighttpd.conf.orig',
                                       stop    => 'chkconfig lighttpd off;service lighttpd stop',
                                       start   => 'chkconfig lighttpd on;service lighttpd restart',
                                       save    => 1},
                   'lighttpduser'  => {fetch   => '/etc/lighttpd/lighttpd.user',
                                       default => '/etc/lighttpd/lighttpd.user.orig',
                                       stop    => 'chkconfig lighttpd off;service lighttpd stop',
                                       start   => 'chkconfig lighttpd on;service lighttpd restart',
                                       save    => 1},
                   'modbus'        => {fetch   => '/etc/stacfg/modbus.xml',
                                       default => '/etc/stacfg/modbus.xml.orig',
                                       stop    => 'chkconfig modbus off;service modbus stop',
                                       start   => 'chkconfig modbus on;service modbus restart &>/dev/null;xsltproc --stringparam clichanges /etc/stacfg/modbus.xml /home/httpd/jbmconfig/conf/rev_modbus.xsl /home/httpd/jbmconfig/conf/config.xml > /tmp/config.new;mv -f /tmp/config.new /home/httpd/jbmconfig/conf/config.xml',
                                       save    => 1},
                   'mrouted'       => {fetch   => '/etc/mrouted/mrouted.conf',
                                       default => '/etc/mrouted/mrouted.conf.orig',
                                       stop    => 'chkconfig mrouted off;service mrouted stop',
                                       start   => 'chkconfig mrouted on;service mrouted restart',
                                       save    => 1},
                   'modprobe_conf' => {fetch   => '/etc/modprobe.conf',
                                       default => '/etc/modprobe.conf.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pppoe'         => {fetch   => '/etc/ppp/pppoe.conf',
                                       default => '/etc/ppp/pppoe.conf.orig',
                                       stop    => 'chkconfig adsl off;service adsl stop',
                                       start   => 'chkconfig adsl on;service adsl restart',
                                       save    => 1},
                   'chap'          => {fetch   => '/etc/ppp/chap-secrets',
                                       default => '/etc/ppp/chap-secrets.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pap'           => {fetch   => '/etc/ppp/pap-secrets',
                                       default => '/etc/ppp/pap-secrets.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pppopts'       => {fetch   => '/etc/ppp/options',
                                       default => '/etc/ppp/options.orig',
                                       stop    => '', # FIXME: Add line to jbminit.conf?!
                                       start   => '', # FIXME: Add line to jbminit.conf?!
                                       save    => 1},
                   'pppipsec'      => {fetch   => '/etc/sysconfig/ipsec-ppp',
                                       default => '/etc/sysconfig/ipsec-ppp.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pppoeipsec'      => {fetch   => '/etc/sysconfig/ipsec-pppoe',
                                       default => '/etc/sysconfig/ipsec-pppoe.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pppdialipsec'      => {fetch   => '/etc/sysconfig/ipsec-pppdial',
                                       default => '/etc/sysconfig/ipsec-pppdial.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pppipup'       => {fetch   => '/etc/ppp/ip-up.local',
                                       default => '/etc/ppp/ip-up.local.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'pppipdown'     => {fetch   => '/etc/ppp/ip-down.local',
                                       default => '/etc/ppp/ip-down.local.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'dnsmasq'       => {fetch   => '/etc/dnsmasq/dnsmasq.conf',
                                       default => '/etc/dnsmasq/dnsmasq.conf.example',
                                       stop    => 'chkconfig dnsmasq off;service dnsmasq stop',
                                       start   => 'chkconfig dnsmasq on;service dnsmasq restart',
                                       save    => 1},
                   'jbmwall'       => {fetch   => '/etc/jbmwall.conf',
                                       default => '/etc/jbmwall.conf.orig',
                                       stop    => 'chkconfig iptables off; /sbin/jbmwall stop',
                                       start   => 'chkconfig iptables on; /sbin/jbmwall restart',
                                       save    => 1},
                   'vsftpd'        => {fetch   => '/etc/vsftpd/vsftpd.conf',
                                       default => '/etc/vsftpd/vsftpd.conf.orig',
                                       stop    => 'chkconfig vsftpd off;service xinetd restart',
                                       start   => 'chkconfig vsftpd on; service xinetd restart',
                                       save    => 1},
                   'vsftpd_chroot' => {fetch   => '/etc/vsftpd/vsftpd.chroot_list',
                                       default => '/etc/vsftpd/vsftpd.chroot_list.orig',
                                       stop    => 'chkconfig vsftpd off;service xinetd restart',
                                       start   => 'chkconfig vsftpd on; service xinetd restart',
                                       save    => 1},
                   'vsftpd_user_allow'   => {fetch   => '/etc/vsftpd/vsftpd.user_list',
                                       default => '/etc/vsftpd/vsftpd.user_list.orig',
                                       stop    => 'chkconfig vsftpd off;service xinetd restart',
                                       start   => 'chkconfig vsftpd on; service xinetd restart',
                                       save    => 1},
                   'int_eth0'      => {fetch   => '/etc/sysconfig/network-scripts/ifcfg-eth0',
                                       default => '/etc/sysconfig/network-scripts/ifcfg-eth0.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'int_eth1'      => {fetch   => '/etc/sysconfig/network-scripts/ifcfg-eth1',
                                       default => '/etc/sysconfig/network-scripts/ifcfg-eth1.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipr2_match'    => {fetch   => '/etc/iproute2/ematch_map',
                                       default => '/etc/iproute2/ematch_map.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipr2_field'    => {fetch   => '/etc/iproute2/rt_dsfield',
                                       default => '/etc/iproute2/rt_dsfield.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipr2_proto'    => {fetch   => '/etc/iproute2/rt_protos',
                                       default => '/etc/iproute2/rt_protos.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipr2_realm'    => {fetch   => '/etc/iproute2/rt_realms',
                                       default => '/etc/iproute2/rt_realms.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipr2_scope'    => {fetch   => '/etc/iproute2/rt_scopes',
                                       default => '/etc/iproute2/rt_scopes.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipr2_table'    => {fetch   => '/etc/iproute2/rt_tables',
                                       default => '/etc/iproute2/rt_tables.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipfallback'    => {fetch   => '/etc/jbm/ipfallback.conf',
                                       default => '/etc/jbm/ipfallback.conf.orig',
                                       stop    => 'chkconfig ipfallback off;service ipfallback stop',
                                       start   => 'chkconfig ipfallback on;service ipfallback restart',
                                       save    => 1},
                   #'ipwatcher'     => {fetch   => '/etc/ipwatcher.conf',
                   #                    default => '/etc/ipwatcher.conf.orig',
                   #                    stop    => '',
                   #                    start   => '',
                   #                    save    => 1},
                   'jbminit'       => {fetch   => '/etc/jbm/jbminit.conf',
                                       default => '/etc/jbm/jbminit.conf.orig',
                                       stop    => 'killall -USR2 jbminit',
                                       start   => 'killall -HUP  jbminit',
                                       save    => 1},
                   'ntpd'          => {fetch   => '/etc/ntp.conf',                          
                                       default => '/etc/ntp.conf.orig',                     
                                       stop    => 'chkconfig ntpd off; service ntpd stop',  
                                       start   => 'chkconfig ntpd on; service ntpd restart',
                                       save    => 1},
                   'smcroute'       => {fetch   => '/etc/smcroute/smcroute.conf',
                                       default => '/etc/smcroute/smcroute.conf.orig',
                                       stop    => 'chkconfig smcroute off;service smcroute stop',
                                       start   => 'chkconfig smcroute on;service smcroute restart',
                                       save    => 1},
                   'sysctl'        => {fetch   => '/etc/sysctl.conf',
                                       default => '/etc/sysctl.conf.orig',
                                       stop    => 'sysctl -e -p /etc/sysctl.conf',
                                       start   => 'sysctl -e -p /etc/sysctl.conf',
                                       save    => 1},
                   'pimd'          => {fetch   => '/etc/pimd/pimd.conf',
                                       default => '/etc/pimd/pimd.conf.orig',
                                       stop    => 'chkconfig pimd off;service pimd stop',
                                       start   => 'chkconfig pimd on;service pimd restart',
                                       save    => 1},
                   'pingalive1'    => {fetch   => '/etc/jbm/ping_alive.conf',
                                       default => '/etc/jbm/ping_alive.conf.orig',
                                       stop    => 'chkconfig ping_alive off;service ping_alive stop',
                                       start   => 'chkconfig ping_alive on;service ping_alive restart',
                                       save    => 1},
                   'pingalive2'    => {fetch   => '/etc/jbm/ping_alive2.conf',
                                       default => '/etc/jbm/ping_alive2.conf.orig',
                                       stop    => 'chkconfig ping_alive off;service ping_alive stop',
                                       start   => 'chkconfig ping_alive on;service ping_alive restart',
                                       save    => 1},
                   'routemon'      => {fetch   => '',
                                       default => '',
                                       stop    => 'chkconfig routemon off;service routemon stop',
                                       start   => 'chkconfig routemon on;service routemon restart',
                                       save    => 1},
                   'bgpd'          => {fetch   => '/etc/zebra/bgpd.conf',
                                       default => '/etc/zebra/bgpd.conf.sample',
                                       stop    => 'chkconfig bgpd off;service bgpd stop',
                                       start   => 'chkconfig bgpd on;service bgpd restart',
                                       save    => 1},
                   'ospfd'         => {fetch   => '/etc/zebra/ospfd.conf',
                                       default => '/etc/zebra/ospfd.conf.sample',
                                       stop    => 'chkconfig ospfd off;service ospfd stop',
                                       start   => 'chkconfig ospfd on;service ospfd restart',
                                       save    => 1},
                   'ramqtt'        => {fetch   => '/etc/ramqtt/conf.json',
                                       default => '/etc/ramqtt/conf.json',
                                       stop    => 'chkconfig ramqtt off;service ramqtt stop',
                                       start   => 'chkconfig ramqtt on;service ramqtt restart',
                                       save    => 1},
                   'ripd'          => {fetch   => '/etc/zebra/ripd.conf',
                                       default => '/etc/zebra/ripd.conf.sample',
                                       stop    => 'chkconfig ripd off;service ripd stop',
                                       start   => 'chkconfig ripd on;service ripd restart',
                                       save    => 1},
                   'zebra'         => {fetch   => '/etc/zebra/zebra.conf',
                                       default => '/etc/zebra/zebra.conf.sample',
                                       stop    => 'chkconfig zebra off;service zebra stop',
                                       start   => 'chkconfig zebra on;service zebra restart',
                                       save    => 1},
                   'snmpd'         => {fetch   => '/etc/snmp/snmpd.conf',
                                       default => '/etc/snmp/snmpd.conf.sample',
                                       stop    => 'chkconfig snmpd off;service snmpd stop',
                                       start   => 'chkconfig snmpd on;service snmpd restart',
                                       save    => 1},
                   'snproxyconf'   => {fetch   => '/etc/lighttpd/snproxy.conf',
                                       default => '/etc/lighttpd/snproxy.conf.orig',
                                       stop    => 'chkconfig snproxy off;service snproxy stop',
                                       start   => 'chkconfig snproxy on;service snproxy restart',
                                       save    => 1},
                   'snproxy2conf'   => {fetch   => '/etc/lighttpd/snproxy2.conf',
                                       default => '/etc/lighttpd/snproxy2.conf.orig',
                                       stop    => 'chkconfig snproxy2 off;service snproxy2 stop',
                                       start   => 'chkconfig snproxy2 on;service snproxy2 restart',
                                       save    => 1},
                   'snproxy3conf'   => {fetch   => '/etc/lighttpd/snproxy3.conf',
                                       default => '/etc/lighttpd/snproxy3.conf.orig',
                                       stop    => 'chkconfig snproxy3 off;service snproxy3 stop',
                                       start   => 'chkconfig snproxy3 on;service snproxy3 restart',
                                       save    => 1},
                   'snproxy4conf'   => {fetch   => '/etc/lighttpd/snproxy4.conf',
                                       default => '/etc/lighttpd/snproxy4.conf.orig',
                                       stop    => 'chkconfig snproxy4 off;service snproxy4 stop',
                                       start   => 'chkconfig snproxy4 on;service snproxy4 restart',
                                       save    => 1},
                   'snproxy5conf'   => {fetch   => '/etc/lighttpd/snproxy5.conf',
                                       default => '/etc/lighttpd/snproxy5.conf.orig',
                                       stop    => 'chkconfig snproxy5 off;service snproxy5 stop',
                                       start   => 'chkconfig snproxy5 on;service snproxy5 restart',
                                       save    => 1},
                   'snproxy6conf'   => {fetch   => '/etc/lighttpd/snproxy6.conf',
                                       default => '/etc/lighttpd/snproxy6.conf.orig',
                                       stop    => 'chkconfig snproxy6 off;service snproxy6 stop',
                                       start   => 'chkconfig snproxy6 on;service snproxy6 restart',
                                       save    => 1},
                   'snproxy7conf'   => {fetch   => '/etc/lighttpd/snproxy7.conf',
                                       default => '/etc/lighttpd/snproxy7.conf.orig',
                                       stop    => 'chkconfig snproxy7 off;service snproxy7 stop',
                                       start   => 'chkconfig snproxy7 on;service snproxy7 restart',
                                       save    => 1},
                   'snproxy8conf'   => {fetch   => '/etc/lighttpd/snproxy8.conf',
                                       default => '/etc/lighttpd/snproxy8.conf.orig',
                                       stop    => 'chkconfig snproxy8 off;service snproxy8 stop',
                                       start   => 'chkconfig snproxy8 on;service snproxy8 restart',
                                       save    => 1},
                   'snproxy9conf'   => {fetch   => '/etc/lighttpd/snproxy9.conf',
                                       default => '/etc/lighttpd/snproxy9.conf.orig',
                                       stop    => 'chkconfig snproxy9 off;service snproxy9 stop',
                                       start   => 'chkconfig snproxy9 on;service snproxy9 restart',
                                       save    => 1},
                   'snproxy10conf'   => {fetch   => '/etc/lighttpd/snproxy10.conf',
                                       default => '/etc/lighttpd/snproxy10.conf.orig',
                                       stop    => 'chkconfig snproxy10 off;service snproxy10 stop',
                                       start   => 'chkconfig snproxy10 on;service snproxy10 restart',
                                       save    => 1},
                   'snproxyuser'   => {fetch   => '/etc/lighttpd/snproxy.user',            
                                       default => '/etc/lighttpd/snproxy.user.orig',
                                       stop    => 'chkconfig snproxy off;service snproxy stop',
                                       start   => 'chkconfig snproxy on;service snproxy restart',
                                       save    => 1},
                   'sxdnpdrv'      => {fetch   => '/etc/stacfg/sxdnpdrv.ini',
                                       default => '/etc/stacfg/sxdnpdrv.ini.orig',
                                       stop    => 'chkconfig sxdnpdrv off;service sxdnpdrv stop',
                                       start   => 'chkconfig sxdnpdrv on;service sxdnpdrv restart',
                                       save    => 1},
                   'eventd'        => {fetch   => '/etc/eventd/events.conf',
                                       default => '/etc/eventd/events.conf.sample',
                                       stop    => 'chkconfig eventd off;service eventd stop',
                                       start   => 'chkconfig eventd on;service eventd restart',
                                       save    => 1},
                   'rclocal'       => {fetch   => '/etc/rc.d/rc.local',
                                       default => '/etc/rc.d/rc.local.orig',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'ipsec_conf'    => {fetch   => '/etc/ipsec/ipsec.conf',
                                       default => '/etc/ipsec/ipsec.conf.orig',
                                       stop    => 'chkconfig ipsec off;service ipsec stop',
                                       start   => 'chkconfig ipsec on;service ipsec restart',
                                       save    => 1},
                   'ipsec_sec'     => {fetch   => '/etc/ipsec/ipsec.secrets',
                                       default => '/etc/ipsec/ipsec.secrets.orig',
                                       stop    => 'chkconfig ipsec off;service ipsec stop',
                                       start   => 'chkconfig ipsec on;service ipsec restart',
                                       save    => 1},
                   'openvpncli'     => {fetch   => '/etc/openvpn/client.conf',
                                       default => '/etc/openvpn/client.conf.orig',
                                       stop    => 'chkconfig openvpn off;service openvpn stop',
                                       start   => 'chkconfig openvpn on;service openvpn restart',
                                       save    => 1},
                   'openvpnsrv'     => {fetch   => '/etc/openvpn/server.conf',
                                       default => '/etc/openvpn/server.conf.orig',
                                       stop    => 'chkconfig openvpn off;service openvpn stop',
                                       start   => 'chkconfig openvpn on;service openvpn restart',
                                       save    => 1},
               'openvpn_cfgparse'  => {fetch   => "$openvpn_parse_cfg_name",
                                       default => "$openvpn_parse_cfg_name.orig",
                                       stop    => "chkconfig openvpn off;service openvpn stop",
                                       start   => "(openvpn_cl_parser.pl --file $openvpn_parse_cfg_name) && (chkconfig openvpn on;service openvpn restart &>/dev/null) || false",
                                       save    => 1},
                   'openvpnauthpass'=> {fetch   => '/etc/openvpn/authpass',
                                       default => '/etc/openvpn/authpass.orig',
                                       stop    => 'chkconfig openvpn off;service openvpn stop',
                                       start   => 'chkconfig openvpn on;service openvpn restart',
                                       save    => 1},
                   'sdk'           => {fetch   => '/etc/jbm/sdk.conf',
                                       default => '/etc/jbm/sdk.conf.orig',
                                       stop    => 'service sdk stop',
                                       start   => 'service sdk restart',
                                       save    => 1},
                   'ssh_conf'      => {fetch   => '/etc/ssh/ssh_config',
                                       default => '/etc/ssh/ssh_config.sample',
                                       stop    => '',
                                       start   => '',
                                       save    => 1},
                   'sshd_conf'     => {fetch   => '/etc/ssh/sshd_config',
                                       default => '/etc/ssh/sshd_config.orig',
                                       stop    => 'chkconfig sshd off;service sshd stop',
                                       start   => 'chkconfig sshd on;service sshd restart',
                                       save    => 1},
                   'iptables'      => {fetch   => '/etc/sysconfig/iptables',
                                       default => '/etc/sysconfig/iptables.orig',
                                       stop    => 'chkconfig iptables off;service iptables stop',
                                       start   => 'chkconfig iptables on;service iptables restart',
                                       save    => 1},
                   'statrt'        => {fetch   => '/etc/sysconfig/static-routes',
                                       default => '/etc/sysconfig/static-routes.orig',
                                       stop    => '',
                                       start   => 'service network restart',
                                       save    => 1},
                   'svmclient'     => {fetch   => '/etc/jbm/svmclient.conf',
                                       default => '/etc/jbm/svmclient.conf.orig',
                                       stop    => 'svmclient remove',
                                       start   => 'svmclient',
                                       save    => 1},
                   'syslog'        => {fetch   => '/etc/sysconfig/syslog',
                                       default => '/etc/sysconfig/syslog.orig',
                                       stop    => 'service syslog stop',
                                       start   => 'service syslog restart',
                                       save    => 1},
                   'stunnelcli'    => {fetch   => '/etc/stunnel/stunnelcli.conf',
                                       default => '/etc/stunnel/stunnelcli.conf-sample',
                                       stop    => 'unsetstunnel stunnelcli.conf',
                                       start   => 'setstunnel stunnelcli.conf',
                                       save    => 1},
                   'stunnelsrv'    => {fetch   => '/etc/stunnel/stunnelsrv.conf',
                                       default => '/etc/stunnel/stunnelsrv.conf-sample',
                                       stop    => 'unsetstunnel stunnelsrv.conf',
                                       start   => 'setstunnel stunnelsrv.conf',
                                       save    => 1},
                   'vnstat'        => {fetch   => '/etc/vnstat/vnstat.conf',
                                       default => '/etc/vnstat/vnstat.conf.orig',
                                       stop    => 'chkconfig vnstat off;service vnstat stop',
                                       start   => 'chkconfig vnstat on;service vnstat restart',
                                       save    => 1},
                   'vrrpd'         => {fetch   => '/etc/vrrpd/vrrpd.conf',
                                       default => '/etc/vrrpd/vrrpd.conf.orig',
                                       stop    => 'chkconfig vrrpd off;service vrrpd stop',
                                       start   => 'chkconfig vrrpd on;service vrrpd restart',
                                       save    => 1},
                    'vrrpd2'        => {fetch   => '/etc/vrrpd/vrrpd2.conf',
                                       default => '/etc/vrrpd/vrrpd2.conf.orig',
                                       stop    => 'chkconfig vrrpd2 off;service vrrpd2 stop',
                                       start   => 'chkconfig vrrpd2 on;service vrrpd2 restart',
                                       save    => 1},
                   'jbmcontrol'    => {fetch   => '/home/jbmgatew/jbmcontrol.conf',
                                       default => '/home/jbmgatew/jbmcontrol.conf.orig',
                                       stop    => 'killall jbmcontrol',
                                       start   => '/bin/jbmcontrol',
                                       save    => 1},
                   'serialip_cfg'  => {fetch   => '/home/jbmgatew/unit.xml',
                                       default => '/home/jbmgatew/unit.xml',
                                       stop    => 'killall jbmcontrol',
                                       start   => '/bin/jbmcontrol',
                                       save    => 1}
                  );


my %REQUEST = ();


ReadParse(\%REQUEST);


# Do we have everything we need from the input?

if (! exists($REQUEST{action})) {
	IOG::CGI::sendError("Missing action");
	exit 1;
}

if (! exists($REQUEST{SubSystem})) {
	IOG::CGI::sendError("Missing SubSystem");
	exit 1;
}

# Do we have everything we need internally?

if (! exists($sub_systems{$REQUEST{SubSystem}})) {
	IOG::CGI::sendError("Subsystem not found");
	exit 1;
}

if (! exists($sub_systems{$REQUEST{SubSystem}}->{$REQUEST{action}})) {
	IOG::CGI::sendError("Missing action for subsystem");
	exit 1;
}

# Done with validation, no exit until final response is sent

if ($REQUEST{action} eq 'fetch' || $REQUEST{action} eq 'default') {
	($RESPONSE{error}, $RESPONSE{message}, $RESPONSE{data}) =
		&doReadConf($REQUEST{SubSystem}, $REQUEST{action});
}
elsif ($REQUEST{action} eq 'stop' || $REQUEST{action} eq 'start') {
	($RESPONSE{error}, $RESPONSE{message}) =
		&doRunService($REQUEST{SubSystem}, $REQUEST{action});
}
elsif ($REQUEST{action} eq 'save') {
	if (exists($REQUEST{FileContents})) {
		($RESPONSE{error}, $RESPONSE{message}) =
			&doSave($REQUEST{SubSystem}, $REQUEST{FileContents});
	}
	else {
		$RESPONSE{error} = 1;
		$RESPONSE{message} = "Missing FileContents";
	}
}
else {
	$RESPONSE{error} = 1;
	$RESPONSE{message} = "Invalid action";
}

IOG::CGI::sendJson(\%RESPONSE);

exit;

sub doReadConf {
	my $SubSystem = shift;
	my $action = shift;
	my $filename = $sub_systems{$SubSystem}->{$action};
	my $error = 0;
	my $message = "";
	my $data = "";

	if ( $filename =~ /^\s*$/ ) {
		$message = "This option does not have a config file.  Start/Stop Only.";
	}
	elsif (open(FILE, $filename)) {
		foreach my $line (<FILE>) {
			$data .= $line
		}
		close(FILE);
	}
	else {
		$message = "Unable to open file '$filename' - $!";
		$error = 1;
	}

	return ($error, $message, $data);
}

sub doSave {
	my $SubSystem = shift;
	my $FileContents = shift;
	my $fetch_file = $sub_systems{$SubSystem}->{fetch};
	my $default_file = $sub_systems{$SubSystem}->{default};
	my $error = 0;
	my $message = "";

	if ( $fetch_file =~ /^\s*$/ ) {
		$message = "This option does not use a config file.  Nothing to save.";
	}
	else {
		# Save original fetch_file as default if missing.
		if (! -e $default_file) {
			system("cp", $fetch_file, $default_file);
		}
		# dos2unix
		$FileContents =~ s/\r\n/\n/g;
		if (open(FFILE, ">", $fetch_file)) {
			print FFILE $FileContents;
			close(FFILE);
		}
		else {
			$error = 1;
			$message = "Failed to write $fetch_file";
		}
	}
	return ($error, $message)
}

# Remove color codes and nonprintable characters from service start/stop strings
sub doRunService {
	my $SubSystem = shift;
	my $action = shift;
	my $message = `($sub_systems{$SubSystem}->{$action}) 2>&1`;
	my $error = $?;
	my @lines = split(/\n/, $message);

	for (@lines) {
		chomp;
		s/\e\[\d+(?>(;\d+)*)m//g;
		s/[^[:print:]]//g;
		s/\[60G//g;
	}
	$message = join("\n", @lines);

	if ($error == 0) {
		$message .= "\n\nOperation SUCCESS";
	}
	else {
		$message .= "\n\nOperation FAILED";
		$error = 1;
	}

	return ($error, $message)
}
