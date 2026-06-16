#!/usr/bin/perl -w
# (C)2018 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion
# logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All
# other company and product names are trademarks of their respective owners.

require "./gau-profile-acl.pl";
require "./uploadlib.pl";
require "./jsonlib.pl";
require "/etc/env2/env2.pl";

my $MANAGER = "/usr/iog/bin/tags";
my %JSON_RESPONSE = (
	"error" => 0
);

my %in = ();
ReadParseUpload(\%in);

sub send_response {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%JSON_RESPONSE);
}

sub send_error {
	my $msg = shift;
	$JSON_RESPONSE{error} = 1;
	$JSON_RESPONSE{message} = $msg;
	&send_response();
	exit;
}

sub require_access {
	my $action = shift;
	my $allowed = profileAclAccess($ENV{REMOTE_USER}, "tags");

	if ($allowed ne "write") {
		if ($action eq "write" or $allowed eq "none") {
			&send_error("User '$ENV{REMOTE_USER}' not authorized to $action tags");
		}
	}
}

# read_file: Return file contents as a string
sub read_file {
	my $filename = @_[0];
	my $filestring = "";
	local $/ = undef;
	if (open(FH, $filename)) {
		$filestring = <FH>;
		close(FH);
	}
	return $filestring;
}

sub write_file {
	my ($filename, $contents) = @_;
	if (open(FH, ">", $filename)) {
		print FH $contents;
		close(FH);
	}
}

# export print contents of all tag lists for download as a file
#     This prints custom mime-type headers to discourage the browser from trying
#     to render the contents then calls tags_manager.pl to print a concatenated
#     list of tags from the user, model, status lists
#
#     Finally, we exit to prevent additional data from being printed and included
#     in the export
sub export {
	print "Content-Type:application/x-download\n";
	print "Content-Disposition:attachment;filename=tags.csv\n\n";
	system("$MANAGER export");
	# Bail out to prevent any further data from being sent as the file
	exit 0;
}

sub export_straton {
	print "Content-Type:application/x-download\n";
	print "Content-Disposition:attachment;filename=tags_straton.csv\n\n";
	system("$MANAGER export --straton");
	# Bail out to prevent any further data from being sent as the file
	exit 0;
}

if (exists($in{query})) {
	if ($in{query} eq "get") {
		require_access("read");
		$JSON_RESPONSE{csv} = `$MANAGER export`;
	}
	elsif ($in{query} eq "set") {
		require_access("write");
		if (exists($in{csv})) {
			chomp( my $import = `mktemp` );
			&write_file($import, $in{csv});
			system("$MANAGER import $import");
			unlink($import);
		}
		# Send back what we received as confirmation
		$JSON_RESPONSE{csv} = `$MANAGER export`;
	}
	elsif ($in{query} eq "export") {
		require_access("read");
		&export();
	}
	elsif ($in{query} eq "export_straton") {
		require_access("read");
		&export_straton();
	}
	elsif ($in{query} eq "import" or $in{query} eq "merge") {
		require_access("write");
		if (! exists($in{filename}) || ! -f $in{filename}) {
			&send_error("Missing File");
		}
		system($MANAGER, $in{query}, $in{filename});
		unlink($in{filename});
	}
	elsif ($in{query} eq "reset") {
		require_access("write");
		system("$MANAGER reset");
	}
	else {
		&send_error("Unrecognized query");
	}
}
else {
	&send_error("Unrecognized options");
}

&send_response();

exit;

