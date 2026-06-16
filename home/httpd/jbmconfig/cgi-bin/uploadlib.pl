#!/usr/bin/perl -w
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# CGI upload-helper library
#
# Routines:
#    ReadParseUpload - Call this instead of a cgi-lib.pl ReadParse to clean up
#                      after lighttpd and masquerade incoming filenames
#
#    UploadParse - Use this in existing scripts that do their own ReadParse
#                  Does not call ReadParse, but takes the same arguments

require "./cgi-lib.pl";

sub UploadParse {
	# Variable initialization mirrors cgi-lib.pl
	local (*in) = shift if @_;
	local (*incfn,
			*inct,
			*insfn) = @_;
	local $nameKey = "";

	# Find the variable with our uploaded file:
	while (($k, $v) = each %in) {
		if (-f $v) {
			$nameKey = $k;
			break;
		}
	}
	if ($nameKey eq "") {
		return;
	}
	# If we were passed a valid name for the file, use it
	if (exists($incfn{$nameKey}) && $incfn{$nameKey} !~ /[&|$;"']/) {
		rename($in{$nameKey}, "/tmp/$incfn{$nameKey}");
		$in{$nameKey} = "/tmp/$incfn{$nameKey}";
	}
}

sub ReadParseUpload {
	# Variable initialization mirrors cgi-lib.pl
	local (*in) = shift if @_;
	local (*incfn,
			*inct,
			*insfn) = @_;

	# Call cgi-lib *Parse to get the file names
	&ReadParse(\%in, \%incfn, \%inct, \%insfn);
	&UploadParse(\%in, \%incfn, \%inct, \%insfn);
}


1;
