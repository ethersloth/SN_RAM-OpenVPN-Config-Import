#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

#
# v1.00	Initial write
# bet
#
# argv1 - string to search for
# argv2 - file contents to append into /etc/modprobe.conf
#
#
#

my $MIN_SEARCH_LENGTH = "10";
my $ORIG_MODRPOBE_FILE = "/etc/modprobe.conf";

#file must be in /tmp for protection
my $TMP_DIR = "/tmp";

my $random_chars = &gen_random_chars(10);
my $new_tmp_file = "$TMP_DIR/$random_chars.temp";

chomp(@ARGV);

my ( $search_string, $tmp_file ) = @ARGV;

#get rid of garbage characters, .aybe
#$search_string =~ s/[^a-zA-Z0-9_-]//g;

if ( length($search_string) < int($MIN_SEARCH_LENGTH) )
{
	print "Error: Search string \"$search_string\" is not at least $MIN_SEARCH_LENGTH chars long\n";
	exit(1);
}

if ( $tmp_file =~ /^\s*$/ ) 
{
	print "Error: Temp content file is empty.\n";
	exit(1);
}

#remove directory structure
$tmp_file =~ s/^[\.\/].*\///g;
$tmp_file = "$TMP_DIR/$tmp_file";

if ( ! -e "$tmp_file" )
{
	print "Error: $tmp_file does not exist.\n";
	exit(1);
}

if (  "$tmp_file" eq "$new_tmp_file" )
{
	print "Error: you cannot use the file name $new_tmp_file.\n";
	exit(1);
}

#All good, take modprobe.conf and get rid of the search string,
#and put it in a new file
system("grep -v '$search_string' $ORIG_MODRPOBE_FILE > $new_tmp_file");

#now append the file with the new file
system("cat $tmp_file >> $new_tmp_file");

#replace the old .conf file with the new one
system("cp -f $new_tmp_file $ORIG_MODRPOBE_FILE ");

#unlink the temp files
unlink("$tmp_file");
unlink("$new_tmp_file");

exit(0);

sub gen_random_chars()
{
   my $password;
   my $_rand;

   my $password_length = $_[0];
   if (!$password_length)
   {
      $password_length = 10;
   }

   my @chars = split(" ",
   "a b c d e f g h i j k l m n o
   p q r s t u v w x y z
   0 1 2 3 4 5 6 7 8 9");

   srand;

   for (my $i=0; $i <= $password_length ;$i++)
   {
      $_rand = int(rand 41); 
      $password .= $chars[$_rand];
   }

   return $password;
}


