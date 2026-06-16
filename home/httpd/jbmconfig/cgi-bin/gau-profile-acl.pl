#!/usr/bin/perl

# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

# profileAclAccess( <user>, <subsystem> );
# @returns "write", "read", or "none"

sub profileAclAccess ($$) {
	my $user = shift;
	my $subsystem = shift;
	my $access = "none";

	if ($user !~ /^\w+$/ or $subsystem !~ /^\w+$/) {
		system("logger -t gau-profile-acl.pl 'Malformed user or subsystem in ACL check'");
		return "none";
	}

	if ($user eq "admin") {
		return "write";
	}

	# profile.xml has an access="" attribute of the form /AC?L?/i
	# corresponding to the following users. Capital means write-access

	my $aclquery = "/home/httpd/jbmconfig/bin/xpeval -s"
			. " --in=/home/httpd/jbmconfig/conf/profile.xml";
	my $usrkey;
	my $subkey;

	if ($user eq "gauser") {
		$usrkey = 'C'
	}
	elsif ($user eq "techsup") {
		$usrkey = 'L'
	}
	else {
		system("logger -t gau-profile-acl.pl 'Unknown user $user checking access'");
	}

	if ($usrkey) {
		$aclquery .= " --xpath='/profile/subsystems/subsystem[\@name=\"$subsystem\"]/\@access'";
		$subkey = `$aclquery`;

		if ($subkey =~ /$usrkey/) {
			$access = "write";
		}
		elsif ($subkey =~ /$usrkey/i) {
			$access = "read";
		}
		else {
			$access = "none";
		}
	}
	else {
		$access = "none";
	}

	return $access;
}

1;
