#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

# Script to list all files and delete selected files and erase all directories on device

require "./cgi-lib.pl";
require "./jsonlib.pl";

my $INTERNAL_SMSLOG = "/datalog/smslog";
my $SMS_DIR = "/tmp/sms";

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
	my $path = $INTERNAL_SMSLOG;
	my $file = "";

	if ($name !~ /^[a-z0-9\-._]+$/i) {
		&sendError("Invalid log name");
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
	$RESPONSE{internal} = &getFileStatsList( $INTERNAL_SMSLOG );
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
		else {
			&sendError("Unrecognized query");
		}
	}
	elsif ($in{query} eq "list") {
		&listLogs();
	}
	elsif ($in{query} eq "rotate") {
		#Send Rotate command to SMS handler
		my $RET = system("killall -USR1 smscmd &>/dev/null");
		if ( 0 != $RET) {
			&sendError("Failed to send rotate log command");
		}
	}
	elsif ($in{query} eq "test") {
		if (! exists $in{number}) {
			&sendError("Missing number");
		}
		if (! exists $in{message}) {
			&sendError("Missing message");
		}
		&sendTestMessage($in{number}, $in{message});
	}
	elsif ($in{query} eq "testwait") {
		if (! exists $in{id} or $in{id} !~ m/^[0-9a-z-._ ]+$/i) {
			&sendError("Missing message id");
		}
		&watchTestMessage($in{id});
	}
	else {
		&sendError("Unrecognized query");
	}
}
else {
	&sendError("Must specify a query");
}

&sendResponse();

exit 0;



sub sendTestMessage {
	my $number = shift;
	my $message = shift;
	my $queue_dir = "$SMS_DIR/send";
	system("mkdir --parents \"$queue_dir\"");
	# Create temporary file on same filesystem - will use atomic move after writing
	chomp(my $queue_file = `mktemp "$queue_dir.XXXXXX"`);

	open(my $qfh, ">", $queue_file) or &sendError("Failed to write message queue");
	print $qfh <<"EOF";
TO=$number
MSG=$message
EOF
	close($qfh);

	system("mv \"$queue_file\" \"$queue_dir\"");
	$RESPONSE{id} = $queue_file;
	$RESPONSE{id} =~ s/^.*\///;
}

sub watchTestMessage {
	my $msg_id = shift;
	my $timeout = 60;
	my $dh;

	$RESPONSE{message} = "Missing message";

	while ($timeout-- > 0) {
		if (opendir $dh, "$SMS_DIR/send_ok") {
			while (my $_ = readdir $dh) {
				if ($_ =~ m/^$msg_id/) {
					$RESPONSE{message} = "Message sent successfully";
					return;
				}
			}
			closedir($dh);
		}
		if (opendir $dh, "$SMS_DIR/send_fail") {
			while (my $_ = readdir $dh) {
				if ($_ =~ m/^$msg_id/) {
					$RESPONSE{error} = 1;
					$RESPONSE{message} = "Message failed to send";
					return;
				}
			}
			closedir($dh);
		}
		sleep 1;
	}
}
