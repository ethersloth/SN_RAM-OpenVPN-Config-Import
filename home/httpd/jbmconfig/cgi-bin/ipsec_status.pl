#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

#version 1.04;

$ENV{PATH} .= ":/home/httpd/jbmconfig/bin:/sbin:/usr/bin";

my $html_output = 0;
my $cgilib = "/home/httpd/jbmconfig/cgi-bin/cgi-lib.pl";
if ( -e "$cgilib" )
{
	require "$cgilib";

	if (&ReadParse(\%my_vars, \%cgi_cfn,\%cgi_ct,\%cgi_sfn))
	{
		if ( $my_vars{'html'}  )
		{
			$html_output = 1;
		}
	}
}

my $main_cmd = "ipsec auto --status";

my $output = `$main_cmd 2>&1`;
my @output = split/\n/, $output;

my %h_conns;
my $conns_href = \%h_conns;
#name
#state
#networkline

#get all the connectios into a hash of hashes
foreach(@output)
{
	chomp;
	if ( $_ =~ /^0+\s+\"(.*)\":\s+.*$/ )
	{
		my $conn_name;
		( $conn_name = $1 ) =~ s/\s+//g;
		$conns_href->{ $conn_name }->{ name } = "$conn_name";
		$conns_href->{ $conn_name }->{ state } = "DOWN";
		
	}
}
#get the state
#foreach my $line(reverse(@output))
#{
	for my $conn_name ( keys %$conns_href )
	{
	    foreach my $line(reverse(@output))
	    {
		if ( $line =~ m/$conn_name\"/ )
		{
			if ( $line =~ /established/i )
			{
				$conns_href->{ $conn_name }->{ state } = "UP";
				next;
			}
			elsif (  
				$line =~ /unrouted/ ||
				$line =~ /eroute eclipsed/ ||
				$line =~ /prospective erouted/ ||
				$line =~ /erouted HOLD/ ||
				$line =~ /fail erouted/ ||
				$line =~ /keyed, unrouted/
			      )
			{
				$conns_href->{ $conn_name }->{ state } = "DOWN";
			}
			elsif ($line =~ /newest ISAKMP SA: #([0-9]+); newest IPsec SA: #([0-9]+);/)
			{
				if ($conns_href->{ $conn_name }->{ state } eq "UP")
				{
					# Check if tunnel is only half-up
					if ($1 == 0 && $2 != 0)
					{
						$conns_href->{ $conn_name }->{ state } = "DOWN-UP";
					}
					elsif ($1 != 0 && $2 == 0)
					{
						$conns_href->{ $conn_name }->{ state } = "UP-DOWN";
					}
				}
			}
			
			if ( $line =~ /\.\.\./ )
			{
				my @tmp = split/;/, $line;  
				my @tmp2 = split /:/, $tmp[0]; 
				($conns_href->{ $conn_name }->{ network } = $tmp2[1]) =~ s/\s+//g;
				last;
			}
		}
	    }
	}
#}

if ( 1 == $html_output )
{
	print "Expires: Mon, 26 Jul 1997 05:00:00 GMT\n";
	print "Last-Modified: " . gmtime() . " GMT\n";
	print "Cache-Control: no-store, no-cache, must-revalidate\n";
	print "Cache-Control: post-check=0, pre-check=0\n";
	print "Pragma: no-cache\n";
	print "Content-type: text/html\n\n";
}
else
{
	print "\n\n";
}
for my $k1 ( sort { ($h_conns{$a} <=> $h_conns{$b}) || ($h_conns{$a} cmp $h_conns{$b}) } keys %$conns_href )
{
	print "$conns_href->{ $k1 }{ name }:$conns_href->{ $k1 }{ state }";
	print ":$conns_href->{ $k1 }{ network }\n";
}

