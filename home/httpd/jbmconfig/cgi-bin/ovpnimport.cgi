#!/usr/bin/perl
use strict;
use warnings;
require "./cgi-lib.pl";
require "./uploadlib.pl";
require "./jsonlib.pl";

sub log_msg {
    my ($msg) = @_;
    system("logger", "-t", "ovpnimport.cgi", $msg);
}

my %response = (
    error => 0,
    message => ""
);

my %in;
ReadParseUpload(\%in);

my $query = $in{query} || "";
log_msg("request query=$query");

if ($query eq "install") {
    install_config(\%in, \%response);
} elsif ($query eq "list") {
    list_profiles(\%response);
} elsif ($query eq "ccd_upload") {
    ccd_upload(\%in, \%response);
} elsif ($query eq "connect") {
    connect_profile(\%in, \%response);
} elsif ($query eq "disconnect") {
    disconnect_profile(\%in, \%response);
} elsif ($query eq "delete") {
    delete_profile(\%in, \%response);
} elsif ($query eq "mgmt_command") {
    mgmt_command(\%in, \%response);
} elsif ($query eq "validate") {
    validate_config(\%in, \%response);
} else {
    $response{error} = 1;
    $response{message} = "Unknown query: $query";
}

print "Content-type: text/html; charset=utf8\n\n";
print JSON_Serialize(\%response);
exit 0;

sub normalize_filename {
    my ($filename) = @_;
    
    # Remove directory traversal attempts
    $filename =~ s/[\/\\]//g;
    
    # Convert .ovpn to .conf
    $filename =~ s/\.ovpn$/.conf/i;
    
    # Ensure .conf extension
    $filename =~ s/\.conf$/.conf/i;
    if ($filename !~ /\.conf$/) {
        $filename .= ".conf";
    }
    
    # Strip special characters, keep only alphanumeric, dash, underscore, dot
    $filename =~ s/[^a-zA-Z0-9._-]/_/g;
    
    # Remove leading/trailing dots and dashes
    $filename =~ s/^[.-]+//;
    $filename =~ s/[.-]+$//;
    
    return $filename;
}

sub normalize_profile_name {
    my ($profile) = @_;
    $profile ||= "";
    $profile =~ s/[\/\\]//g;
    $profile =~ s/[^a-zA-Z0-9._-]/_/g;
    if ($profile !~ /\.conf$/) {
        $profile .= ".conf";
    }
    return $profile;
}

sub profile_is_connected {
    my ($profile_name) = @_;
    my $base = $profile_name;
    $base =~ s/\.conf$//;
    my $pid_file = "/var/run/openvpn/$base.pid";

    return 0 if (!-f $pid_file);
    if (open(my $pfh, "<", $pid_file)) {
        my $pid = <$pfh>;
        close($pfh);
        chomp($pid);
        if ($pid && kill(0, $pid)) {
            return 1;
        }
    }
    return 0;
}

sub find_openvpn_binary {
    my @locations = (
        "/sbin/openvpn",
        "/usr/sbin/openvpn",
        "/usr/local/sbin/openvpn"
    );
    foreach my $loc (@locations) {
        return $loc if -x $loc;
    }
    return "";
}

sub validate_content {
    my ($content) = @_;
    my @required = qw(remote proto ca);
    my $found_required = 0;
    
    # Check for OpenVPN directives
    if ($content =~ /^(remote|proto|ca|cert|key|mode|dev|cipher|auth)/m) {
        $found_required = 1;
    }
    
    # Reject if looks like binary
    my $binary_chars = $content =~ tr/\x00-\x08\x0B-\x0C\x0E-\x1F//;
    if ($binary_chars > 0) {
        return (0, "File appears to be binary or corrupted");
    }
    
    # Reject if empty
    if (length($content) < 50) {
        return (0, "File is too small to be a valid OpenVPN config");
    }
    
    if (!$found_required) {
        return (0, "File does not contain valid OpenVPN directives");
    }
    
    return (1, "");
}

sub install_config {
    my ($params, $response_ref) = @_;
    
    my $config_file = $params->{file};
    my $config_name = "imported_config";
    if ($config_file =~ m{/tmp/([^/]+)$}) {
        $config_name = $1;
    }
    
    if (!$config_file) {
        log_msg("install failed: no uploaded file field");
        $response_ref->{error} = 1;
        $response_ref->{message} = "No configuration file uploaded";
        return;
    }
    log_msg("install start: upload_path=$config_file");
    
    # Read uploaded file
    my $content = "";
    if (open(my $fh, "<", $config_file)) {
        while (my $line = <$fh>) {
            $content .= $line;
        }
        close($fh);
    } else {
        log_msg("install failed: cannot read uploaded file $config_file");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to read uploaded file";
        return;
    }
    
    # Validate content
    my ($valid, $error_msg) = validate_content($content);
    if (!$valid) {
        log_msg("install failed: validation error $error_msg");
        $response_ref->{error} = 1;
        $response_ref->{message} = $error_msg;
        return;
    }
    
    # Determine target filename
    my $target_filename = $config_name || "imported_config";
    $target_filename = normalize_filename($target_filename);
    
    # Ensure .conf extension
    $target_filename =~ s/\.conf$/.conf/;
    if ($target_filename !~ /\.conf$/) {
        $target_filename .= ".conf";
    }
    
    # Target path
    my $target_path = "/etc/openvpn/" . $target_filename;
    
    # Check if file already exists
    if (-f $target_path) {
        # Backup existing file
        my $backup_path = $target_path . ".bak";
        system("cp", $target_path, $backup_path);
    }
    
    # Write to target location
    if (open(my $fh, ">", $target_path)) {
        print $fh $content;
        close($fh);
        
        # Set permissions (readable by openvpn, writable by root)
        system("chmod", "600", $target_path);
        system("chown", "root:root", $target_path);
        
    } else {
        log_msg("install failed: cannot write $target_path");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to write configuration to device";
        return;
    }
    
    # Restart OpenVPN service (SN units use init.d scripts)
    my $restart_output = `/etc/init.d/openvpn restart 2>&1`;
    if ($? != 0) {
        $restart_output = `service openvpn restart 2>&1`;
    }
    my $restart_status = $?;
    
    if ($restart_status != 0) {
        log_msg("install wrote $target_path, restart warning: $restart_output");
        # Log warning but don't fail - file was written successfully
        # Service restart might fail for various reasons (e.g., configuration errors)
        $response_ref->{error} = 0;
        $response_ref->{message} = "Configuration installed but service restart returned: $restart_output";
        $response_ref->{filename} = $target_filename;
    } else {
        log_msg("install success: wrote $target_path and restarted service");
        $response_ref->{error} = 0;
        $response_ref->{message} = "Configuration installed and OpenVPN service restarted";
        $response_ref->{filename} = $target_filename;
        $response_ref->{service_output} = $restart_output;
    }
}

sub list_profiles {
    my ($response_ref) = @_;
    
    my @profiles = ();
    
    # List all .conf files in /etc/openvpn/
    if (opendir(my $dh, "/etc/openvpn")) {
        while (my $entry = readdir($dh)) {
            next unless $entry =~ /\.conf$/;
            
            my $file_path = "/etc/openvpn/$entry";
            next unless -f $file_path;
            
            my @stat = stat($file_path);
            my $size = $stat[7] || 0;
            my $mode = sprintf("%04o", $stat[2] & 07777);
            my ($is_server, $has_ccd) = profile_details($file_path);
            
            push @profiles, {
                filename => $entry,
                size => $size,
                mode => $is_server ? "server" : "client",
                perm => $mode,
                is_server => $is_server,
                has_ccd => $has_ccd,
                connected => profile_is_connected($entry)
            };
        }
        closedir($dh);
    }
    
    # Sort by filename
    @profiles = sort { $a->{filename} cmp $b->{filename} } @profiles;
    
    $response_ref->{error} = 0;
    $response_ref->{data} = \@profiles;
    $response_ref->{message} = "Listed " . scalar(@profiles) . " profile(s)";
}

sub connect_profile {
    my ($params, $response_ref) = @_;

    my $profile = normalize_profile_name($params->{profile});
    my $profile_path = "/etc/openvpn/$profile";

    if (!-f $profile_path) {
        $response_ref->{error} = 1;
        $response_ref->{message} = "Profile not found: $profile";
        return;
    }

    if (profile_is_connected($profile)) {
        $response_ref->{error} = 0;
        $response_ref->{message} = "Profile already connected: $profile";
        return;
    }

    my $openvpn_bin = find_openvpn_binary();
    if (!$openvpn_bin) {
        log_msg("connect failed: OpenVPN binary not found for profile=$profile");
        $response_ref->{error} = 1;
        $response_ref->{message} = "OpenVPN binary not found";
        return;
    }

    if (!-d "/var/run/openvpn") {
        mkdir "/var/run/openvpn";
    }

    my $base = $profile;
    $base =~ s/\.conf$//;
    my $pid_file = "/var/run/openvpn/$base.pid";
    unlink($pid_file);

    my $cmd = "$openvpn_bin --daemon --writepid $pid_file --config $profile --cd /etc/openvpn 2>&1";
    my $output = `cd /etc/openvpn && $cmd`;
    my $status = $?;

    if ($status != 0 || !profile_is_connected($profile)) {
        log_msg("connect failed: profile=$profile status=$status output=$output");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to connect profile: $profile. $output";
        return;
    }

    if (!-f "/var/lock/subsys/openvpn") {
        system("touch", "/var/lock/subsys/openvpn");
    }

    $response_ref->{error} = 0;
    $response_ref->{message} = "Profile connected: $profile";
    log_msg("connect success: profile=$profile");
}

sub disconnect_profile {
    my ($params, $response_ref) = @_;

    my $profile = normalize_profile_name($params->{profile});
    my $base = $profile;
    $base =~ s/\.conf$//;
    my $pid_file = "/var/run/openvpn/$base.pid";

    if (!-f $pid_file) {
        $response_ref->{error} = 0;
        $response_ref->{message} = "Profile already disconnected: $profile";
        log_msg("disconnect noop: profile already disconnected profile=$profile");
        return;
    }

    my $pid = "";
    if (open(my $pfh, "<", $pid_file)) {
        $pid = <$pfh>;
        close($pfh);
        chomp($pid);
    }

    if ($pid) {
        kill("TERM", $pid);
    }

    unlink($pid_file);

    if (profile_is_connected($profile)) {
        log_msg("disconnect failed: profile still connected profile=$profile");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to disconnect profile: $profile";
        return;
    }

    my $remaining_pid_count = 0;
    if (opendir(my $pdh, "/var/run/openvpn")) {
        while (my $entry = readdir($pdh)) {
            if ($entry =~ /\.pid$/) {
                $remaining_pid_count++;
            }
        }
        closedir($pdh);
    }

    if ($remaining_pid_count == 0 && -f "/var/lock/subsys/openvpn") {
        unlink("/var/lock/subsys/openvpn");
    }

    $response_ref->{error} = 0;
    $response_ref->{message} = "Profile disconnected: $profile";
    log_msg("disconnect success: profile=$profile");
}

sub delete_profile {
    my ($params, $response_ref) = @_;

    my $profile = normalize_profile_name($params->{profile});
    my $profile_path = "/etc/openvpn/$profile";

    if (!$profile || !-f $profile_path) {
        log_msg("delete failed: profile not found profile=$profile");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Profile not found: $profile";
        return;
    }

    if (profile_is_connected($profile)) {
        my %disc_response = ();
        disconnect_profile({ profile => $profile }, \%disc_response);
        if ($disc_response{error}) {
            log_msg("delete failed: unable to stop connected profile=$profile");
            $response_ref->{error} = 1;
            $response_ref->{message} = "Unable to stop running profile before delete: $profile";
            return;
        }
    }

    if (!unlink($profile_path)) {
        log_msg("delete failed: unlink failed profile=$profile path=$profile_path");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to delete profile: $profile";
        return;
    }

    my $backup_path = $profile_path . ".bak";
    if (-f $backup_path) {
        unlink($backup_path);
    }

    $response_ref->{error} = 0;
    $response_ref->{message} = "Profile deleted: $profile";
    log_msg("delete success: profile=$profile");
}

sub validate_config {
    my ($params, $response_ref) = @_;
    
    my $config_file = $params->{file};
    
    if (!$config_file) {
        $response_ref->{error} = 1;
        $response_ref->{message} = "No configuration file uploaded";
        return;
    }
    
    # Read uploaded file
    my $content = "";
    if (open(my $fh, "<", $config_file)) {
        while (my $line = <$fh>) {
            $content .= $line;
        }
        close($fh);
    } else {
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to read uploaded file";
        return;
    }
    
    # Validate content
    my ($valid, $error_msg) = validate_content($content);
    
    if (!$valid) {
        $response_ref->{error} = 1;
        $response_ref->{message} = $error_msg;
    } else {
        $response_ref->{error} = 0;
        $response_ref->{message} = "Configuration is valid";
    }
}

sub sanitize_mgmt_command {
    my ($cmd) = @_;
    $cmd ||= "";
    $cmd =~ s/[\r\n]+/ /g;
    $cmd =~ s/^\s+//;
    $cmd =~ s/\s+$//;
    return $cmd;
}

sub profile_details {
    my ($file_path) = @_;
    my $is_server = 0;
    my $has_ccd = 0;
    my $fh;

    if (!open($fh, "<", $file_path)) {
        return (0, 0);
    }

    while (my $line = <$fh>) {
        $line =~ s/[\r\n]+$//;
        $line =~ s/^\s+//;
        $line =~ s/\s+$//;
        next if !$line;
        next if $line =~ /^[#;]/;

        if ($line =~ /^(mode\s+server|server\s+|tls-server\b)/i) {
            $is_server = 1;
        }

        if ($line =~ /^client-config-dir\s+(.+)$/i) {
            my $ccd = $1;
            $ccd =~ s/^\s+//;
            $ccd =~ s/\s+$//;
            $ccd =~ s/["']//g;
            if ($ccd eq "ccd" || $ccd eq "/etc/openvpn/ccd") {
                $has_ccd = 1;
            }
        }
    }

    close($fh);
    return ($is_server, $has_ccd);
}

sub sanitize_ccd_filename {
    my ($name) = @_;
    $name ||= "";
    $name =~ s/[\/\\]//g;
    $name =~ s/[^a-zA-Z0-9._-]/_/g;
    $name =~ s/^\.+//;
    return $name;
}

sub ccd_upload {
    my ($params, $response_ref) = @_;

    my $upload_path = $params->{file};
    if (!$upload_path || !-f $upload_path) {
        log_msg("ccd upload failed: missing upload path");
        $response_ref->{error} = 1;
        $response_ref->{message} = "No CCD file uploaded";
        return;
    }

    my $ccd_name = "";
    if ($upload_path =~ m{/tmp/([^/]+)$}) {
        $ccd_name = $1;
    }
    $ccd_name = sanitize_ccd_filename($ccd_name);
    if (!$ccd_name) {
        log_msg("ccd upload failed: invalid filename from upload path=$upload_path");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Invalid CCD filename";
        return;
    }

    my $content = "";
    if (open(my $fh, "<", $upload_path)) {
        while (my $line = <$fh>) {
            $content .= $line;
        }
        close($fh);
    } else {
        log_msg("ccd upload failed: cannot read upload path=$upload_path");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to read CCD upload";
        return;
    }

    if (!-d "/etc/openvpn/ccd") {
        system("mkdir", "-p", "/etc/openvpn/ccd");
    }

    if (!-d "/etc/openvpn/ccd") {
        log_msg("ccd upload failed: mkdir /etc/openvpn/ccd failed");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to create /etc/openvpn/ccd";
        return;
    }

    my $target = "/etc/openvpn/ccd/" . $ccd_name;
    if (open(my $out, ">", $target)) {
        print $out $content;
        close($out);
        system("chmod", "600", $target);
        system("chown", "root:root", $target);
    } else {
        log_msg("ccd upload failed: cannot write target=$target");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to write CCD file";
        return;
    }

    $response_ref->{error} = 0;
    $response_ref->{message} = "CCD file uploaded: $ccd_name";
    $response_ref->{filename} = $ccd_name;
    log_msg("ccd upload success: file=$ccd_name target=$target");
}

sub read_socket_data {
    my ($socket, $timeout_secs, $max_bytes) = @_;
    $timeout_secs ||= 1;
    $max_bytes ||= 65536;
    my $data = "";

    while (1) {
        my $read_mask = "";
        my $fd = fileno($socket);
        last if !defined($fd);
        vec($read_mask, $fd, 1) = 1;

        my $ready = select($read_mask, undef, undef, $timeout_secs);
        last if !$ready;

        my $buf = "";
        my $read = sysread($socket, $buf, 2048);
        last if !defined($read) || $read <= 0;
        $data .= $buf;
        last if length($data) >= $max_bytes;
    }

    return $data;
}

sub shell_quote {
    my ($value) = @_;
    $value = '' if !defined($value);
    $value =~ s/'/'"'"'/g;
    return "'" . $value . "'";
}

sub find_telnet_binary {
    my @paths = (
        "/bin/telnet",
        "/usr/bin/telnet"
    );

    foreach my $path (@paths) {
        return $path if -x $path;
    }

    return "";
}

sub run_mgmt_via_telnet {
    my ($host, $port, $password, $command) = @_;

    my $telnet_bin = find_telnet_binary();
    return (0, "Telnet client not available on device") if !$telnet_bin;

    my $fifo = "/tmp/ovpnimport_mgmt_$$.in";
    my $outfile = "/tmp/ovpnimport_mgmt_$$.out";
    my @lines = ();
    push @lines, $password if defined($password) && $password ne "";
    push @lines, $command;
    push @lines, "quit";
    my $input = join("\n", @lines) . "\n";

    my $script =
        "rm -f " . shell_quote($fifo) . " " . shell_quote($outfile) . "; " .
        "mkfifo " . shell_quote($fifo) . "; " .
        shell_quote($telnet_bin) . " " . shell_quote($host) . " " . shell_quote($port) .
        " < " . shell_quote($fifo) . " > " . shell_quote($outfile) . " 2>&1 & " .
        "telnetpid=\$!; " .
        "sleep 1; " .
        "{ printf %s " . shell_quote($input) . "; sleep 2; } > " . shell_quote($fifo) . "; " .
        "rm -f " . shell_quote($fifo) . "; " .
        "wait \$telnetpid; " .
        "cat " . shell_quote($outfile) . "; " .
        "rm -f " . shell_quote($outfile);

    my $cmd = "sh -c " . shell_quote($script);
    my $output = `$cmd`;

    $output ||= "";
    return (1, $output);
}

sub mgmt_command {
    my ($params, $response_ref) = @_;

    my $host = $params->{host} || "127.0.0.1";
    my $port = $params->{port} || "7505";
    my $password = defined($params->{password}) ? $params->{password} : "";
    my $command = sanitize_mgmt_command($params->{command});

    if (!$host || $host !~ /^[a-zA-Z0-9._:-]+$/) {
        log_msg("mgmt command failed: invalid host host=$host");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Invalid management host";
        return;
    }

    if ($port !~ /^\d+$/ || $port < 1 || $port > 65535) {
        log_msg("mgmt command failed: invalid port port=$port");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Invalid management port";
        return;
    }

    if (!$command) {
        log_msg("mgmt command failed: missing command");
        $response_ref->{error} = 1;
        $response_ref->{message} = "No management command provided";
        return;
    }

    my ($ok, $combined) = run_mgmt_via_telnet($host, $port, $password, $command);

    if (!$ok && $combined =~ /Telnet client not available on device/i) {
        log_msg("mgmt command failed: telnet client unavailable");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Telnet client unavailable on device";
        return;
    }

    $combined ||= "";
    $combined =~ s/\r//g;

    my $has_mgmt_banner = ($combined =~ />INFO:OpenVPN Management Interface Version|Management Interface for OpenVPN/i) ? 1 : 0;

    if (!$has_mgmt_banner && $combined =~ /(Unable to connect|Connection refused|can't connect|No route to host|telnet: can't|failed to connect)/i) {
        log_msg("mgmt command failed: connect failed host=$host port=$port");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Failed to connect to management socket $host:$port";
        $response_ref->{output} = $combined;
        return;
    }

    if ($has_mgmt_banner && $combined =~ /Connection closed by foreign host/i) {
        # Normal telnet close after the management daemon sends its output.
        $combined =~ s/.*?\n(Connection closed by foreign host\.?\s*)$//ms;
    }

    if ($combined =~ /(enter .*password|password:)/i && $password eq "") {
        log_msg("mgmt command failed: password required host=$host port=$port");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Management interface requires a password";
        $response_ref->{output} = $combined;
        return;
    }

    if ($combined =~ /(bad password|auth failed|failed password|incorrect password)/i) {
            log_msg("mgmt command failed: password rejected host=$host port=$port");
            $response_ref->{error} = 1;
            $response_ref->{message} = "Management password rejected";
            $response_ref->{output} = $combined;
            return;
    }

    if ($combined =~ /(ERROR:|AUTH_FAILED|bad password|Unknown command|not understood)/i) {
        log_msg("mgmt command failed: command=$command");
        $response_ref->{error} = 1;
        $response_ref->{message} = "Management command failed: $command";
        $response_ref->{output} = $combined;
        return;
    }

    if (!$has_mgmt_banner) {
        log_msg("mgmt command failed: no management banner host=$host port=$port");
        $response_ref->{error} = 1;
        $response_ref->{message} = "No valid response from management socket";
        $response_ref->{output} = $combined;
        return;
    }

    $response_ref->{error} = 0;
    $response_ref->{message} = "Management command completed: $command";
    $response_ref->{output} = $combined;
    log_msg("mgmt command success: command=$command");
}
