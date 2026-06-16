#!/usr/bin/perl
# (c)2016 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo
# and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company
# and product names are trademarks of their respective owners.


sub html_start()
{

my ($help) = $_[0];

my ($func) = $_[1];

#this must be sent with a \n\n at the end
print "Content-type: text/html; charset=utf8\n\n";

print <<HTML;
<html>
<head>
<title>Sixnet Gateway Administration Utility</title>

<SCRIPT LANGUAGE="JavaScript">


function confirm_ex()
{
    msg = "Are you sure you want to continue?";

    return confirm(msg);

}

//   ##############  SIMPLE  BROWSER SNIFFER
if (document.layers)
{
   navigator.family = "nn4"
}
if (document.all)
{
   navigator.family = "ie4"
}
if (window.navigator.userAgent.toLowerCase().match("gecko"))
{
   navigator.family = "gecko"
}

descarray = new Array(
HTML

   my @array = &getHelp($help);
   my @temp;

   my $first = 1;

   foreach my $i (@array)
   {
      @temp = split("::", $i);

      if ($first == 1)
      {
         $first = 0;

print <<HTML;
"$temp[1]"
HTML
      }
      else
      {
print <<HTML;
,"$temp[1]"
HTML

      }


   }


print <<HTML;
);



overdiv="0";
//  #########  CREATES POP UP BOXES
function popLayer(a)
{
   if (!descarray[a])
   {
      descarray[a]="<font color=red>This popup (#"+a+") isn't setup correctly - needs description</font>";
   }

   if (navigator.family == "gecko")
   {
      pad="0"; bord="1 bordercolor=black";
   }
   else
   {
      pad="1";
      bord="0";
   }

   desc = "<table cellspacing=0 cellpadding="+pad+" border="+bord+"  bgcolor=000000><tr><td>"\n
	+ "<table cellspacing=0 cellpadding=3 border=0 width=100%><tr><td bgcolor=ffffdd><center><font size=-1>"\n
	+ descarray[a]
	+ "</td></tr></table>"\n
	+ "</td></tr></table>";

   if(navigator.family =="nn4")
   {
      document.object1.document.write(desc);
      document.object1.document.close();
      document.object1.left=x+15;
      document.object1.top=y-5;
   }
   else if(navigator.family =="ie4")
   {
      object1.innerHTML=desc;
      object1.style.pixelLeft=x+15;
      object1.style.pixelTop=y-5;
   }
   else if(navigator.family =="gecko")
   {
      document.getElementById("object1").innerHTML=desc;
      document.getElementById("object1").style.left=x+15;
      document.getElementById("object1").style.top=y-5;
   }
}

function resubmit()
{
    document.gwref.submit();
}

function hideLayer()
{
   if (overdiv == "0")
   {
      if (navigator.family =="nn4")
      {
         eval(document.object1.top="-500");
      }
      else if (navigator.family =="ie4")
      {
         object1.innerHTML="";
      }
      else if (navigator.family =="gecko")
      {
         document.getElementById("object1").style.top="-500";
      }
   }
}

//  ########  TRACKS MOUSE POSITION FOR POPUP PLACEMENT
var isNav = (navigator.appName.indexOf("Netscape") !=-1);

function handlerMM(e)
{
   x = (isNav) ? e.pageX : event.clientX + document.body.scrollLeft;
   y = (isNav) ? e.pageY : event.clientY + document.body.scrollTop;
}

if (isNav)
{
   document.captureEvents(Event.MOUSEMOVE);
}

document.onmousemove = handlerMM;
//  End -->

</script>


</head>

<body BGCOLOR="#FFFFFF" LINK="#0000FF" ALINK="#0000FF" VLINK="#0000FF" onload="$func">

<div id="object1" style="position:absolute; background-color:FFFFDD;color:black;border-color:black;border-width:20; visibility:show; left:25px; top:-100px; z-index:+1" onmouseover="overdiv=1;"  onmouseout="overdiv=0; setTimeout('hideLayer()',1000)">
pop up description layer
</div>
HTML

}



sub html_end()
{
print <<HTML;
</body>
</html>
HTML

}


sub linkIcon
{
   my $name = $_[0];
   my $width = $_[1];

   my $file = $name . ".cgi";
   my $img = $name . ".gif";

   my $desc = &getDesc($file);
   my $imglink = &getImage($img);

print <<FORM;
      <td width=$width><p align="center"><a href="/cgi-bin/$file">$imglink</a></p><p align="center">$desc</p></td>
FORM

}

#description of link
sub getDesc
{
   my $file = $_[0];
   my $desc;

   open(HANS, $file);
   @temps = <HANS>;
   close(HANS);

   #$temps[2] is third line of file where comment always is
   ($desc = $temps[2]) =~ s/#//g;

   return $desc;
}

#Image for link
sub getImage
{

   my $name = $_[0];
   my $alt =~ s/\.*\w*//i;
   my $img = "/img/" . $name;
   my $imglink = "<img src=\"$img\" alt=\"$alt\" />";

   return $imglink;


}

sub get_chkconfig
{
	chomp $_;
	my @output = `/sbin/chkconfig --list | /bin/grep \"$_[0]\"`;
	chomp @output;
	if ( $output[0] =~ /^.*\s3:on\s.*$/ )
	{
		return $TRUE;
	}
	return $FALSE;

}

sub toggle_chkconfig
{
	chomp $_;
	my @output = `/sbin/chkconfig --list | /bin/grep \"$_[0]\"`;
	chomp @output;
	if ( $output[0] =~ /^.*\s3:on\s.*$/ )
	{
		system("/sbin/chkconfig $_ off");
	}
	else
	{
		system("/sbin/chkconfig $_ on");
	}


}


# check if a v4 IP is formatted properly
#returns 1 if the IP is valid
#must be x.x.x.x
#octet must be from 0 to 255
#octet can be only 0, but not start with 0
sub checkIP
{
      return $_[0] =~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/  &&
      $1 >= 0 && $1 <= 255 && $1 !~ /^0\d+$/ &&
      $2 >= 0 && $2 <= 255 && $2 !~ /^0\d+$/ &&
      $3 >= 0 && $3 <= 255 && $3 !~ /^0\d+$/ &&
      $4 >= 0 && $4 <= 255 && $4 !~ /^0\d+$/;
}

sub checkDNS
{

   return $_[0] =~ /[A-Za-z0-9\.\-]/;

}

sub checkPort
{
   return $_[0] =~ /^(\d{1,5})$/ &&
                  $1 >= 0 && $1 <= 65535;
}

#figure out the network or broadcast address:
#
sub calcIP
{
     my $type = $_[0]; #broadcast or network
     my $ipaddr = $_[1];
     my $netmask = $_[2];

     my $ipcalc =  "/bin/ipcalc --$type $ipaddr $netmask";
     open (IPCALC,"$ipcalc |");
     $/ = undef;
     my $output = <IPCALC>;
     $/ = "\n";
     close(IPCALC);
     chomp $output;
     my @array = split "=", $output;

     return $array[1];

}


#checks that an IPV4 mask is valid
sub check_mask()
{
        my $ip = $_[0];
        my @list = ( 255,254,252,248,240,224,192,128,0 );

        chomp($ip);
        @octets = split/\./, $ip;
        foreach $octet(@octets)
        {
                my $valid = 0;
                foreach $num(@list)
                {
                        if ( $num eq $octet )
                        {
                                $valid = 1;
                                last;
                        }
                }
                if ( !$valid )
                {
                        return 0;
                }
        }

        #now chech that each octet to the right of a non
        #255 octet is 0
        for ( my $i =0; $i < 4; $i++ )
        {
                if ( 255 != int($octets[$i]) )
                {
                        if ( 0 != int($octets[$i+1])  )
                        {
                                return 0;
                        }
                }
        }

        return 1;
}


sub wizardseq
{

   my $file = $_[0];
   my $current = $_[1];
   my $color = "bgcolor=#00ff00";
   my $currentpage = 0;

   open(HAN, "/home/httpd/jbmconfig/cgi-bin/$file.list");
   my @temp = <HAN>;
   close(HAN);

   chomp(@temp);

   my $size = @temp;

   for (my $i = 0; $i < $size; $i++)
   {

      if ($current eq $temp[$i])
      {
         if ($i == 0)
         {
            $nextpage = $temp[1];
print <<ROUTE;
   <br>
   <table align="center" width="80%" border="1">
    <tr>


ROUTE
            foreach my $j (@temp)
            {
               if ($j eq $current)
               {
                  $color = "bgcolor=#ff0000";
                  $currentpage = 1;

               }
               elsif ($currentpage == 1)
               {
                  $color = "";
               }

               print "<td $color><div align=\"center\"><a style=\"color:0000ff\" href=\"/cgi-bin/$j?w=wizard\">$j</a></div></td>";
            }

print <<ROUTE;

      <td width="7%"><a style=color:0000ff href="/cgi-bin/$nextpage?w=wizard"><IMG SRC="/icons/nextarrow.jpg"></a></td>
    </tr>
  </table>
ROUTE

         }
         elsif (($i+1) == $size)
         {
            $prev = $temp[$i - 1];
print <<ROUTE;
   <br>
   <table align="center" width="80%" border="1">
    <tr>
      <td width="7%"><a style=color:0000ff href="/cgi-bin/$prev?w=wizard"><IMG SRC="/icons/prevarrow.jpg"></a></td> 

ROUTE
            foreach my $j (@temp)
            {
               if ($j eq $current)
               {
                  $color = "bgcolor=#ff0000";
                  $currentpage = 1;

               }
               elsif ($currentpage == 1)
               {
                  $color = "";
               }

               print "<td $color><div align=\"center\"><a style=color:0000ff href=\"/cgi-bin/$j?w=wizard\">$j</a></div></td>";
            }

print <<ROUTE;

    </tr>
  </table>
ROUTE

         }
         else
         {
            $nextpage = $temp[$i + 1];
            $prev = $temp[$i - 1];
print <<ROUTE;
   <br>
   <table align="center" width="80%" border="1">
    <tr>
      <td width="7%"><a style=color:0000ff href="/cgi-bin/$prev?w=wizard"><IMG SRC="/icons/prevarrow.jpg"></a></td>
ROUTE
            foreach my $j (@temp)
            {
               if ($j eq $current)
               {
                  $color = "bgcolor=#ff0000";
                  $currentpage = 1;

               }
               elsif ($currentpage == 1)
               {
                  $color = "";
               }

               print "<td $color><div align=\"center\"><a style=color:0000ff href=\"/cgi-bin/$j?w=wizard\">$j</a></div></td>";
            }

print <<ROUTE;

      <td width="7%"><a style=color:0000ff href="/cgi-bin/$nextpage?w=wizard"><IMG SRC="/icons/nextarrow.jpg"></a></td>
    </tr>
  </table>
ROUTE
         }
         last;
      }
   }


}

sub getHelp
{

   my $page = $_[0];

   my $flink = "/home/httpd/jbmconfig/cgi-bin/help.txt";
   my @message = ();

   open(HAN, $flink);
   my @help = <HAN>;
   close(HAN);

   chomp(@help);

   foreach my $i (@help)
   {
      if ($i =~ s/^$page://)
      {
         push(@message, $i);
      }

   }

   return @message;

}


sub getGate
{
   my @output = `/bin/ps -ax`;
   my @ret = ();

   chomp(@output);

   $ret[0] = "<div style=\"color:ff0000\">Not Running</div>";
   $ret[1] = "<div style=\"color:0000ff\">Inactive</div>";
   $ret[2] = "<div style=\"color:0000ff\">Inactive</div>";

   foreach my $lines (@output)
   {

      if ($lines =~ /gwlnx/)
      {
         @temp = split(" ", $lines);

         $ret[0] = " <div style=\"color:00ff00\">Running</div> Time up: $temp[3]";
      }

      if ($lines =~ /\/bin\/svmclient/)
      {
         $ret[1] = " <div style=\"color:00ff00\">Active</div>";
      }

      if ($lines =~ /\/bin\/gmu_listener/)
      {
         $ret[2] = " <div style=\"color:00ff00\">Active</div>";
      }
   }

   return @ret;

}


1; # return true
