#!/usr/bin/perl
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet
# are registered trademarks of Red Lion Controls, Inc. All other company and product names are
# trademarks of their respective owners.

require IOG::GetFC;

my $version      = "1.3";
my $new_modemno  = "Unknown Model No.";


if ( $ENV{"FC_MODELNO"} )
{
	my $modelno = $ENV{"FC_MODELNO"};
	my $fc_ram = $ENV{"FC_RAM"};
	my $fc_cpu_id = $ENV{"FC_CPU_ID"};
	my $fc_bluetree = $ENV{"FC_BLUETREE"};

	$new_modemno = "SN Industrial Pro";
	if ( "2" eq "$fc_cpu_id" )
	{
		#TODO: Change this to something that marketing wants
		$new_modemno = "S5T Industrial Pro";
	}

	if ( "1" eq "$fc_bluetree" )
	{
		#its a BT|SN|RAM
		my $stripped_modelno = $modelno;
		$stripped_modelno =~ s/\s*(SN|BT|RAM)\-\s*//;
		$new_modemno = " RAM " . $stripped_modelno;
	}
}

print "$new_modemno";
exit(0);

