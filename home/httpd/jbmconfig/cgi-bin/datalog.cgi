#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Script to list all files and delete selected files and erase all directories on device

require "./cgi-lib.pl";
require "./jsonlib.pl";

my $INTERNAL_DATALOG = "/datalog";
my $SDCARD_DATALOG = "/media/sdcard/datalog";

my %RESPONSE = (
	"error" => 0
);

sub sendResponse {
	print "Content-type: text/html; charset=utf8\n\n";
	print &JSON_Serialize(\%RESPONSE);
	exit
}
sub sendError {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&sendResponse();
}

sub findLog {
	my $name = shift;
	my $savepath = shift;
	my $path = $INTERNAL_DATALOG;
	my $file = "";

	if ($name !~ /^[a-z0-9\-._]+$/i) {
		&sendError("Invalid log name");
	}
	if ($savepath eq "sdcard") {
		$path = $SDCARD_DATALOG;
	}

	$file = "$path/$name";

	if (! -e $file) {
		&sendError("No log found. (It could have rotated, try refreshing)");
	}

	return $file;
}

sub previewLog {
	my $file = shift;
	# The web UI will truncate the file if it's too long. Don't even send the
	# whole file to preserve data.
	if (`/usr/bin/printf \$(/bin/cat $file | /usr/bin/wc -l)` > 20) {
		return `/usr/bin/head -10 $file; /bin/echo "..."; /usr/bin/tail -10 $file`;
	}
	return `/bin/cat $file`;
}

sub exportFile {
	my $logfile = shift;
	my $filename = $logfile;
	$filename =~ s/^.*\/([^\/]+)$/\1/;
	print "Content-Type:application/x-download\n";
	print "Content-Disposition:attachment;filename=$filename\n\n";
	if (open(FILE,"$logfile")) {
		while (<FILE>) {
			print $_;
		}
		close (FILE);
	}
	# exit to prevent any more data from being appended to file
	exit 0;
}

sub removeFile {
	my $file = shift;
	unlink $file;
}

sub getFileStatsList {
	my $path = shift;
	my @fileList = ();
	chomp(my $nameList = `ls $path`);
	foreach (split "\n", $nameList) {
		if (-f "$path/$_") {
			push(@fileList, {(
				size => (stat "$path/$_")[7],
				name => $_
			)});
		}
	}
	return \@fileList;
}

sub listLogs {
	$RESPONSE{internal} = &getFileStatsList( $INTERNAL_DATALOG );
	$RESPONSE{sdcard} = &getFileStatsList( $SDCARD_DATALOG );
}

my %in = ();
ReadParse(\%in);

if (exists($in{query})) {
	if (exists $in{name} and exists $in{savepath}) {
		if ($in{query} eq "preview") {
			$RESPONSE{data} = &previewLog( &findLog($in{name}, $in{savepath}) );
		}
		elsif ($in{query} eq "download") {
			&exportFile( &findLog($in{name}, $in{savepath}) );
		}
		elsif ($in{query} eq "remove") {
			&removeFile( &findLog($in{name}, $in{savepath}) );
		}
		else {
			&sendError("Unrecognized query");
		}
	}
	elsif ($in{query} eq "list") {
		&listLogs();
	}
	else {
		&sendError("Missing name or savepath");
	}
}
else {
	&sendError("Must specify a query");
}

&sendResponse();

exit 0;
