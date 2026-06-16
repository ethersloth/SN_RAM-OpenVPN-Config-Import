#!/usr/bin/perl -w
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Script to list all gatherstats/gatherconfigs files on device

require "./jsonlib.pl";

my %JSON_RESPONSE = (
	"error" => 0
);

@{$JSON_RESPONSE{data}{stats}} = ();
@{$JSON_RESPONSE{data}{auto}} = ();

opendir(DIR, "/tmp");
while (my $f = readdir(DIR)) {
	if ($f =~ /^(configs|stats)[0-9A-Za-z\-._]+\.zip$/) {
		push(@{$JSON_RESPONSE{data}{stats}}, {(
			size => (stat("/tmp/$f"))[7],
			name => $f
		)});
	}
}
closedir(DIR);

opendir(DIR, "/storage");
while (my $f = readdir(DIR)) {
	if ($f =~ /^[0-9]+-stats[0-9A-Za-z\-._]+\.zip$/) {
		push(@{$JSON_RESPONSE{data}{auto}}, {(
			size => (stat("/storage/$f"))[7],
			name => $f
		)});
	}
}
closedir(DIR);

print "Content-type: text/html; charset=utf8\n\n";
print &JSON_Serialize(\%JSON_RESPONSE);

exit;
