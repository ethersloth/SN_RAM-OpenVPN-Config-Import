#!/usr/bin/perl
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.

package JBM_System;

sub new
{
   #my $class = shift;
   #my $self  = {has_wireless => undef,
   #             has_ethernet => undef,
   #             interface_list => undef 
   #            };
   $ENV{PATH} .= '/usr/sbin:/bin:/usr/bin:/sbin';
   return(bless({},shift));
}

##########################################################
#
# HARDWARE INSPECTOR FUNCTIONS...
#
##########################################################

# For now, only works on wireless and 2 Ethernet interfaces
sub GetNetworkInterfaceList
{
   my $self = shift;

   my @list = ();

   # Is there a wireless modem (or PCMCIA/Cardbus slot) on this unit?
   if ($self->HasWireless())
   {
      push(@list,'wls');
   }

   # What ethernet interface(s) is/are available on this unit?
   if ($self->HasEth0())
   {
      push(@list,'eth0');
   }

   if ($self->HasEth1())
   {
      push(@list,'eth1');
   }

   return(@list);
}

sub HasWireless
{
   my $self = shift;

   return($self->HasWavecom() || $self->HasPCMCIA() || $self->HasCardbus());
}

sub HasWavecom
{
   return(-e '/proc/feature_codes/ttyS1_cellmodem');
}

sub HasPCMCIA
{
   return(int(`cat /proc/feature_codes/all | grep -c -i pcmcia`));
}

sub HasCardbus
{
   return(int(`cat /proc/feature_codes/all | grep -c -i cardbus`));
}

sub IsCellCardPresent
{
   my $self = shift;
}

sub GetCellCardType
{
   my $self = shift;
}

sub HasEthernet
{
   my $self = shift;
   my $eth  = shift;

   $eth = 'eth0' unless ($eth);

   return(int(`cat /proc/feature_codes/all | grep -c -i 'eth0 yes'`));
}

sub HasEth0
{
   my $self = shift;
   return($self->HasEthernet('eth0'));
}

sub HasEth1
{
   my $self = shift;
   return($self->HasEthernet('eth1'));
}

sub Syslog
{
   my $self = shift;
   my $message = shift or return;
   my $source = $0;

   my $log_cmd = $self->Which("logger");

   if ($log_cmd)
   {
      $message =~ s/\"/\\\"/g;
      $source  =~ s/^.*\///g;


      system("$log_cmd -t $source \"$message\" > /dev/null 2>&1");
   }
}

sub Which
{
   my $self = shift;
   my $command = shift;
   my $result = '';

   if ($command)
   {
      chomp($command);

      my $which_cmd = "/usr/bin/which";

      if (-x $which_cmd)
      {
         my @sys_command = `$which_cmd $command 2> /dev/null`;
         chomp(@sys_command);

         if ($sys_command[0] !~ /^\s*$/)
         {
            $result = $sys_command[0];
         }
      }
   }

   return($result);
}

sub IsServiceEnabled
{
   my $self = shift;
   my $service = shift;
   my $result = 0;

   if ($service)
   {
      $result = int(`chkconfig --list | grep "$service" | grep -c "3:on"`);
   }

   return($result);
}

sub GetProcessList
{
   my $self = shift;
   my %list = ();
   my @output = `ps -ax --cols 1024`;

   foreach my $line (@output)
   {
      $line =~ s/^\s+//;
      $line =~ s/\s+$//;
      my ($pid,$tty,$stat,$time,$cmd,@args) = split(/\s+/,$line);

      next unless ($pid =~ /^\d+$/);
      next unless ($cmd =~ /^[^\[]/);

      $list{$cmd} = {pid  => $pid,
                     tty  => $tty,
                     stat => $stat,
                     time => $time,
                     args => [@args]};
   }

   return(%list);
}

sub IsProcessRunning
{
   my $self = shift;
   my $process = shift;
   my $result = 0;

   if ($process)
   {
      $result = int(`ps -ax | grep -v grep | grep -c -w "$process"`);
   }

   return($result);
}

sub GetConfigValue
{
   my $self = shift;
   my $file = shift;
   my $name = shift;
   my $result = '';

   if ($file && $name)
   {
      if (open(FILE,$file))
      {
         foreach my $line (<FILE>)
         {
            chomp($line);
            next unless ($line !~ /^\s*$/);
            next unless ($line !~ /^\s*#/);
            next unless ($line =~ /=/);
            my ($parm,@value) = split(/\s*=\s*/,$line);
            next unless ($parm eq $name);
            $result = join("",@value);
            last;
         }
      }
   }

   return($result);
}

sub GetProcessArgs
{
   my $self = shift;
   my $process = shift;
   my @result = ();

   if ($process)
   {
      if ($self->IsProcessRunning($process))
      {
         my %ps = $self->GetProcessList();

         # strip the ps output command to its basename, unless the passed process has '/'s in it.
         if ($process =~ /\//)
         {
            if (exists($ps{$process}))
            {
               @result = @{$ps{$process}->{args}};
            }
         }
         else
         {
            foreach my $cmd (keys(%ps))
            {
               if ($process eq $self->Basename($cmd))
               {
                  @result = @{$ps{$cmd}->{args}};
               }
            }
         }
      }
   }

   return(@result);
}

sub Basename
{
   my $self = shift;
   my $command = shift;
   $command =~ s/.*\///g;
   return($command);
}

sub IsPPPConnected
{
   my $self = shift;
   my $result = 0;

   if ($self->IsProcessRunning("pppd"))
   {
      $result = $self->IsInterfaceUp("ppp0");
   }

   return($result);
}

sub IsInterfaceUp
{
   my $self = shift;
   my $interface = shift;
   my $result = 0;

   if ($interface)
   {
      $result = int(`ifconfig $interface | grep -c -w -i up`);
   }

   return($result);
}

sub GetInterfaceAddress
{
   my $self = shift;
   my $interface = shift;
   my $result = '';

   if ($interface)
   {
      foreach my $line (`/sbin/ifconfig $interface 2>&1`)
      {
         chomp($line);
         if ($line =~ /^\s*inet\saddr:(\d+\.\d+\.\d+\.\d+)\s.*$/)
         {
            $result = $1;
         }
      }
   }

   return($result);
}

sub GetInterfacePeerAddress
{
   my $self = shift;
   my $interface = shift;
   my $result = '';

   if ($interface)
   {
      foreach my $line (`/sbin/ifconfig $interface 2>&1`)
      {
         chomp($line);
         if ($line =~ /^\s*inet\saddr:\d+\.\d+\.\d+\.\d+\s+P\-t\-P:(\d+\.\d+\.\d+\.\d+)\s.*$/i)
         {
            $result = $1;
         }
      }
   }

   return($result);
}

sub GetCellSignalStrength
{
   my $self = shift;
   my $result = -1;

   if (open(FILE,"/var/log/lightbar"))
   {
      $/ = undef;
      my $line = <FILE>;
      close(FILE);
      $/ = "\n";

      if ($line =~ /^(\+CSQ:\s+)(\d+)\,\s+(\d+)\,\s+(\d+)/) 
      {
         #its a sprint box
         #+CSQ: 85, 8, 3
         #
         #Range is 74-110, 255 unknown. Lower is better
         #
         if (int($2) == 255)
         {
            $result = 255;
         }
         elsif (int($2) >= 108)
         {
            $result = 1;
         }
         elsif (int($2) >= 90)
         {
            $result = 3;
         }
         elsif (int($2) >= 81)
         {
            $result = 7;
         }
         elsif (int($2) < 81)
         {
            $result = 15;
         }
      }
      elsif ( $line =~ /^(\+CSQ:\s+)(\d+),\s*(\d+)/ )
      {
         #its a Verizon, 
         #+CSQ: 25, 0
         # or it's a
         # GSM/GPRS unit
         #+CSQ: 21,0  <--- ( NO SPACE IN THERE )
         #
         #Range is 0-31, 99 is unknown. Higher is better
         #
         if ( int($2) == 99 )
         {
            $result = 255;
         }
         elsif (int($2) <= 5)
         {
            $result = 1;
         }
         elsif (int($2) <= 13)
         {
            $result = 3;
         }
         elsif (int($2) <= 22)
         {
            $result = 7;
         }
         elsif (int($2) <= 32)
         {
            $result = 15;
         }
      }
      elsif ($line =~ /^LIGHT:\s*(\d+)/)
      {
         $result = int($1);
      }
   }

   return($result);
}

sub GetSystemUptime
{
   my $self = shift;
   my $format = shift;
   my $result = int(`cat /proc/uptime | awk '{print \$1}'`); # $result now holds the number of seconds since last boot.

   if ($format)
   {
      # format the result for the caller:
   }

   return($result);
}

sub GetInterfaceRXBytes
{
   my $self = shift;
   my $interface = shift;
   my $result = 0;

   if ($interface)
   {
      foreach my $line (`/sbin/ifconfig $interface 2>&1`)
      {
         chomp($line);
         if ($line =~ /^\s*RX\sbytes:(\d+)\s+.*$/)
         {
            $result = $1;
         }
      }
   }

   return($result);
}

sub GetInterfaceTXBytes
{
   my $self = shift;
   my $interface = shift;
   my $result = 0;

   if ($interface)
   {
      foreach my $line (`/sbin/ifconfig $interface 2>&1`)
      {
         chomp($line);
         if ($line =~ /^\s*RX\sbytes:\d+\s+.*TX\sbytes:(\d+)\s.*$/)
         {
            $result = $1;
         }
      }
   }

   return($result);
}

sub Killall
{
   my $self = shift;
   my $proc = shift;
   my $sig  = shift;

   if ($proc)
   {
      $sig = 9 unless ($sig);
      $sig =~ s/\D//g;
      system("killall -$sig $proc");
   }

   if (defined(wantarray))
   {
      return(!$self->IsProcessRunning($proc));
   }
}

1; # so a require succeeds...

# package main;
#
# my $sys = JBM_System->new();
#
# $sys->HasWireless();
# $sys->GetNetworkInterfaceList();
#
# exit;

