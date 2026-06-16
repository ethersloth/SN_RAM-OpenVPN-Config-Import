#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
#
# tags_manager.pl: Gateway between single-file and split-format tag databases

sub usage {
	print "Usage:\n";
	print "    tags_manager.pl export\n";
	print "    tags_manager.pl import <tags file>\n";
}

require "/etc/env2/env2.pl";

my $VERSION = "1.1";
my $HEADER_PREFIX = "# Version";

my $USER_TAGS_FILE = &ENV2_get("ENV2_FILE_TAGS_USER");
my $MODEL_TAGS_FILE = &ENV2_get("ENV2_FILE_TAGS_MODEL");
my $STATUS_TAGS_FILE = &ENV2_get("ENV2_FILE_TAGS_STATUS");

my @HEADERS = (
	"Tag Name",
	"Station Name",
	"Station Number",
	"I/O Type #",
	"I/O Register #",
	"Data Type",
	"Actual Min",
	"Actual Max",
	"Scaled Min",
	"Scaled Max",
	"Engineering Units",
	"Decimals",
	"Off Message",
	"On Message",
	"Description",
	"Retain",
	"Source",
	"Class"
);
my $NAME_INDEX = 0; # Tag Name
my $TYPE_INDEX = 3; # I/O Type #
my $ADDR_INDEX = 4; # I/O Register #

# export print contents of all tag lists to STDOUT with a header
sub export {
	# Map of "type-addr":1 to track exported tags and prevent exporting model tags that have been renamed
	my %exported = ();
	my @tag;
	my $key;
	print "$HEADER_PREFIX $VERSION\n";
	print "# ";
	for my $i (0 ..$#HEADERS) {
		print ", " if ($i != 0);
		print $HEADERS[$i];
	}
	print "\n";
	foreach my $file ($USER_TAGS_FILE, $MODEL_TAGS_FILE, $STATUS_TAGS_FILE) {
		if (open(FH, $file)) {
			while(<FH>) {
				@tag = split(',',$_);
				$key = "$tag[$TYPE_INDEX]-$tag[$ADDR_INDEX]";
				if (! exists($exported{$key})) {
					$exported{$key} = 1;
					print $_;
				}
			}
			close(FH);
		}
	}
}

# check_version - extract version number from first line of file
sub check_version {
	my $vsn = "N/A";
	if (open(my $fh, $_[0])) {
		if (readline($fh) =~ /^$HEADER_PREFIX ([0-9]+\.[0-9]+)/) {
			$vsn = $1;
		}
		close($fh);
	}
	return $vsn;
}

# read_file: Load csv file into specified array
sub read_file {
	my ($filename, $targetList) = @_;
	if (open(FH, $filename)) {
		# Read/parse file into map
		while(my $line = <FH>) {
			chomp($line);
			# Skip comments
			next if ($line =~ /^\s*#/);
			push(@$targetList, [grep(s/^\s+|\s*$//g,split(',', $line))]);
		}
		close(FH);
	}
}

# write_file: Write array to file
sub write_file {
	my ($filename, $targetList) = @_;
	if (open(FH, ">", $filename)) {
		foreach my $entry (@{$targetList}) {
			for my $i (0 .. $#HEADERS) {
				if ($i <= $#{$entry}) {
					if ($i != 0) {
						print FH ","
					}
					print FH "${$entry}[$i]";
				}
			}
			print FH "\n";
		}
		close(FH);
	}
}

# import_file - Split a single tag list into the three user/model/status lists
#     Rules:
#         status list: if a tag matches name or address from this list, it is skipped
#
#         model list:  if a tag matches name, it is skipped, but if the address matches
#                      then the name in the model list is updated (on-board I/O can be renamed)
#
#         user list:   anything that doesn't match the previous lists is added to here
#             note:    duplicate tag names/addresses within this list are not allowed
#                      If they occur in the import file, the FIRST one is preserved
sub import_file {
	my $importFile = shift;
	my @importList = ();
	my $inName;
	my $inType;
	my $inAddr;
	my @userList = ();
	my @modelList = ();
	my @statusList = ();

	&read_file($importFile, \@importList);
	&read_file($MODEL_TAGS_FILE, \@modelList);
	&read_file($STATUS_TAGS_FILE, \@statusList);

	INTAG: foreach my $impTag (@importList) {
		$inName = ${$impTag}[$NAME_INDEX];
		$inType = ${$impTag}[$TYPE_INDEX];
		$inAddr = ${$impTag}[$ADDR_INDEX];
		# Skip anything matched in the status list
		foreach my $tag (@statusList) {
			if ($inName eq ${$tag}[$NAME_INDEX] or ($inType eq ${$tag}[$TYPE_INDEX] and $inAddr eq ${$tag}[$ADDR_INDEX])) {
				next INTAG;
			}
		}
		MODTAG: foreach my $tag (@modelList) {
			if ($inName eq ${$tag}[$NAME_INDEX]) {
				# model tags can be renamed, but the original name cannot be reassigned
				if ($inType ne ${$tag}[$TYPE_INDEX] or $inAddr ne ${$tag}[$ADDR_INDEX]) {
					next INTAG;
				}
				# If anything is different about the tag, add it to user list.
				for my $i (0 .. $#HEADERS) {
					if ($i <= $#{$impTag}) {
						last MODTAG if (${$tag}[$i] ne ${$impTag}[$i]);
					}
				}
			}
			# On-board I/O can be renamed, but they get added as user tags, skip to below
			elsif ($inType eq ${$tag}[$TYPE_INDEX] and $inAddr eq ${$tag}[$ADDR_INDEX]) {
				last;
			}
		}
		# Validate against current user list to make sure we don't get internal duplicates
		#     a match means skip, so the FIRST tag of a kind is kept
		foreach my $tag (@userList) {
			if ($inName eq ${$tag}[$NAME_INDEX] or ($inType eq ${$tag}[$TYPE_INDEX] and $inAddr eq ${$tag}[$ADDR_INDEX])) {
				next INTAG;
			}
		}
		# Else, append new tag to user list
		push(@userList, $impTag);
	}
	&write_file($USER_TAGS_FILE, \@userList);
}

if (scalar(@ARGV) < 1) {
	&usage();
	exit;
}

if ($ARGV[0] eq "export") {
	&export();
}
elsif ($ARGV[0] eq "import") {
	if (scalar(@ARGV) < 2) {
		&usage();
	}
	elsif (! -r $ARGV[1]) {
		print "Can't access file: '$ARGV[1]'\n";
		exit 1;
	}
	else {
		if (&check_version($ARGV[1]) gt $VERSION) {
			print "Import file incompatible with this version";
			exit 1;
		}
		&import_file($ARGV[1]);
	}
}
else {
	&usage();
}
