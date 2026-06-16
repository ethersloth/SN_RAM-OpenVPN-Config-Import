#!/usr/bin/perl

require "./jsonlib.pl";

my %RESPONSE = (
	error => 0
);
my $commonDir = "/etc/common";
my @scriptList = ();
my $scriptName;

if (open(FIND, "find $commonDir -type f |")) {
	while ($scriptName = <FIND>) {
		chomp $scriptName;
		if (-x "$scriptName") {
			$scriptName =~ s/^.*common\///;
			push @scriptList, $scriptName;
		}
	}
	close(FIND);
}

$RESPONSE{data} = \@scriptList;

print "Content-type: text/html; charset=utf8\n\n";
print &JSON_Serialize(\%RESPONSE);

exit;
