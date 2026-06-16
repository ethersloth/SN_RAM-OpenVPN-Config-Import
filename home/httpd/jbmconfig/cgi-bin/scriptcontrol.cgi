#!/usr/bin/perl
# (C)2017 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

use IOG::CGI;
require "./cgi-lib.pl";
require "./jsonlib.pl";

my $storagedir = "/storage/scriptcontrol";
my $SCTLC = "# # SCTL";
my %PIDMAP = ();
my %RESPONSE = (
	error => 0
);
$ENV{PATH} = "/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin";

sub send_response {
	# Not really text/html, but the js expects to do json parsing itself.
	&IOG::CGI::printHeaders({"Content-type" => "text/html"});
	print &JSON_Serialize(\%RESPONSE);
}

sub send_error {
	my $msg = shift;
	$RESPONSE{error} = 1;
	$RESPONSE{message} = $msg;
	&send_response();
	exit 0;
}

sub readFile
{
	my $file = shift;
	open(FILE,"$file") or return "";
	$/ = undef;
	$tmp = <FILE>;
	$/ = "\n";
	close (FILE);
	return $tmp;
}

sub compile {
	my $defines = $_[0];
	my $logic = $_[1];
	my $speed = $_[2];
	my $enable = $_[3];
	my $scriptfile = $_[4];
	my $outputfile = $_[5];
	my $isValid = 1;
	my $usleep = $speed * 1000;
	my $defines_start_line = 0;
	my $logic_start_line = 0;
	open (SCTLF, ">$scriptfile");
	print SCTLF "#!/usr/bin/perl -w\n"
	          . "use strict;\n"
	          . "$SCTLC SPEED $speed\n"
	          . "require \"/etc/jbm/iodblib.pl\";\n"
	          . "require \"/etc/jbm/sctllib.pl\";\n"
	          . "&SetLogFile(\"$outputfile\");\n"
	          . "$SCTLC DEFINES START\n";
	print SCTLF $defines;
	print SCTLF "$SCTLC DEFINES END\n"
	          . "while (1) {\n"
	          . "$SCTLC LOGIC START\n";
	print SCTLF $logic;
	print SCTLF "$SCTLC LOGIC END\n"
	          . "usleep($usleep);\n"
	          . "}\n"
	          . "exit 0;\n";
	close(SCTLF);
	# Get line numbers for replacing any syntax error output below
	open(SCRFILE, "$scriptfile");
	while(<SCRFILE>) {
		if ($_ =~ /$SCTLC DEFINES START/ ) {
			$defines_start_line = $.;
		}
		if ($_ =~ /$SCTLC LOGIC START/ ) {
			$logic_start_line = $.;
		}
	}
	close(SCRFILE);
	chmod(0644, $scriptfile);
	open(OFILE, ">>$outputfile");
	open(CMD, "perl -c $scriptfile 2>&1 |");
	my $modlinenum = 0;
	while(<CMD>) {
		if ( $_ !~ /syntax OK/) {
			$isValid = 0;
		}
		# If line numbers are output, modify them based on our calculated numbers
		if ($_ =~ /line ([0-9]+)/) {
			if ($1 > $defines_start_line && $1 < $logic_start_line) {
				$modlinenum = $1 - $defines_start_line;
				$_ =~ s/line $1/line $modlinenum of your defines/;
			}
			elsif ($1 > $logic_start_line) {
				$modlinenum = $1 - $logic_start_line;
				$_ =~ s/line $1/line $modlinenum of your logic/;
			}
		}
		print OFILE $_;
	}
	close(CMD);
	if ($isValid) {
		print OFILE "Script compiled successfully\n";
		if ($enable eq "yes") {
			chmod(0755, $scriptfile);
		}
	}
	close(OFILE);
}

sub decompile {
	my $scriptfile = $_[0];
	my $isdefines = 0;
	my $islogic = 0;
	my $speed = "";
	my $enable = "no";
	my $defines = "";
	my $logic = "";
	my $var = "";
	my $val = "";
	if (-X "$scriptfile") {
		$enable = "yes";
	}
	open (SCRFILE, "$scriptfile");
	while (<SCRFILE>) {
		if ($_ =~ /$SCTLC ([A-Z]+) ([a-zA-Z0-9]+)/) {
			$var = $1;
			$val = $2;
			if ("SPEED" eq $var && $val =~ /^[0-9]+$/) {
				$speed = $val;
			}
			elsif ("DEFINES" eq $var && "START" eq $val) {
				$isdefines = 1;
			}
			elsif ("DEFINES" eq $var && "END" eq $val) {
				$isdefines = 0;
			}
			elsif ("LOGIC" eq $var && "START" eq $val) {
				$islogic = 1;
			}
			elsif ("LOGIC" eq $var && "END" eq $val) {
				$islogic = 0;
			}
		}
		elsif ($isdefines) {
			$defines .= $_;
		}
		elsif ($islogic) {
			$logic .= $_;
		}
	}
	close (SCRFILE);
	return ($speed, $enable, $defines, $logic)
}

sub decompileConf {
	my $scriptfile = $_[0];
	my $var;
	my $val;
	my $speed = "Unknown";
	my $enable = "no";
	if (-X "$scriptfile") {
		$enable = "yes";
	}
	open (SCRFILE, "$scriptfile");
	while (<SCRFILE>) {
		if ($_ =~ /$SCTLC ([A-Z]+) ([a-zA-Z0-9]+)/) {
			$var = $1;
			$val = $2;
			if ("SPEED" eq $var && $val =~ /^[0-9]+$/) {
				$speed = $val;
			}
		}
	}
	close (SCRFILE);
	return ($speed, $enable);
}

sub printStatus {
	my @statusArray = ();
	my %currentScript;
	if (-d $storagedir) {
		opendir(my($sdir), $storagedir);
		my @list = readdir $sdir;
		closedir($sdir);
		my $cspeed = "";
		my $cenable = "";
		my $cname = "";
		for my $i (0 .. $#list) {
			if ($list[$i] =~ /sctl-([a-zA-Z0-9]+).pl/) {
				%currentScript = ();
				$cname = $1;
				($cspeed, $cenable) = &decompileConf("$storagedir/$list[$i]");
				$currentScript{name} = $cname;
				$currentScript{enable} = $cenable;
				$currentScript{speed} = $cspeed;
				if (exists $PIDMAP{$cname}) {
					$currentScript{status} = "running";
				}
				else {
					$currentScript{status} = "stopped";
				}
				push(@statusArray, \%currentScript);
			}
		}
	}
	$RESPONSE{data} = \@statusArray;
}

sub checkRunningScripts {
	%PIDMAP = ();
	open(CMD, "ps -A -o pid,cmd 2>&1 |");
	while(<CMD>) {
		if ($_ =~ /^\s*([0-9]+)\s+.*sctl-([a-zA-Z0-9]+)\.pl/) {
			$PIDMAP{$2} = $1;
		}
	}
	close(CMD);
}

my %in = ();
ReadParse(\%in);

&checkRunningScripts();

if (exists($in{type}) && exists($in{name})) {
	my $scriptfile = "$storagedir/sctl-$in{name}.pl";
	my $outputfile = "/tmp/sctl-$in{name}.log";
	if ($in{type} eq 'load') {
		my $output = &readFile($outputfile);
		my ($speed, $enable, $defines, $logic) = &decompile($scriptfile);
		$RESPONSE{data}{speed} = $speed;
		$RESPONSE{data}{enable} = $enable;
		$RESPONSE{data}{defines} = $defines;
		$RESPONSE{data}{logic} = $logic;
		$RESPONSE{data}{output} = $output;
	}
	elsif ($in{type} eq 'clear') {
		unlink $outputfile;
	}
	elsif ($in{type} eq 'loadoutput') {
		$RESPONSE{data}{output} = &readFile($outputfile);
	}
	elsif ($in{type} eq 'save') {
		if (! -d $storagedir) {
			mkdir $storagedir;
		}
		&compile($in{func}, $in{loop}, $in{speed}, $in{enable}, $scriptfile, $outputfile);
		$RESPONSE{data} = &readFile($outputfile);
		chmod(0777, $outputfile);
	}
	elsif ($in{type} eq 'start') {
		if (! exists $PIDMAP{$in{name}}) {
			system("/bin/psminder.pl -n '$in{name}' -x 'perl $scriptfile' -c 10 -m 10");
		}
	}
	elsif ($in{type} eq 'stop') {
		if (exists $PIDMAP{$in{name}}) {
			system("kill $PIDMAP{$in{name}} &>/dev/null");
		}
		&checkRunningScripts();
		&printStatus();
	}
	elsif ($in{type} eq 'remove') {
		if (exists $PIDMAP{$in{name}}) {
			system("kill $PIDMAP{$in{name}} &>/dev/null");
		}
		unlink $scriptfile;
		unlink $outputfile;
		&checkRunningScripts();
		&printStatus();
	}
	else {
		&send_error("Unrecognized type");
	}
}
elsif (exists($in{type}) && "status" eq $in{type}) {
	&printStatus();
}
else {
	&send_error("Unrecognized options");
}

&send_response;

exit;
