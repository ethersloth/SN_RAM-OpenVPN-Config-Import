define(["knockout", "GauWeb"], function(ko, GauWeb) {
    "use strict";

    function OvpnImportModel() {
        var self = this;

        self.cfgdata = GauWeb.obj.fileInput({placeholder: "Drag or Drop OpenVPN Profile (.ovpn or .conf)", id: "ovpnimport"});
        self.rawConfig = ko.observable("");
        self.parsedConfig = ko.observable(null);
        self.detectedDirectives = ko.observableArray([]);
        self.embeddedBlocks = ko.observableArray([]);
        self.compatibilityNotes = ko.observableArray([]);
        self.isInstalling = ko.observable(false);
        self.installStatus = ko.observable("");
        self.installSuccess = ko.observable(false);
        self.installedProfiles = ko.observableArray([]);
        self.busyProfile = ko.observable("");
        self.mgmtHost = ko.observable("127.0.0.1");
        self.mgmtPort = ko.observable("7505");
        self.mgmtPassword = ko.observable("");
        self.mgmtCommand = ko.observable("status 3");
        self.mgmtOutput = ko.observable("");
        self.mgmtConnected = ko.observable(false);
        self.isMgmtBusy = ko.observable(false);
        self.mgmtStatus = ko.observable("");
        self.mgmtSuccess = ko.observable(false);
        self.mgmtPollingEnabled = ko.observable(false);
        self.mgmtPollSeconds = ko.observable("5");
        self.mgmtClients = ko.observableArray([]);
        self.busyMgmtClient = ko.observable("");
        self.ccdFileData = GauWeb.obj.fileInput({placeholder: "Select CCD file (client CN filename)", id: "ccd-upload"});
        self.isCcdUploading = ko.observable(false);
        self.ccdStatus = ko.observable("");
        self.ccdSuccess = ko.observable(false);
        var mgmtPollTimer = null;

        self.mgmtClientCount = ko.pureComputed(function() {
            return self.mgmtClients().length;
        });

        self.mgmtTotalRx = ko.pureComputed(function() {
            var total = 0;
            var clients = self.mgmtClients();
            for (var i = 0; i < clients.length; i++) {
                total += parseInt(clients[i].bytesReceived, 10) || 0;
            }
            return total;
        });

        self.mgmtTotalTx = ko.pureComputed(function() {
            var total = 0;
            var clients = self.mgmtClients();
            for (var i = 0; i < clients.length; i++) {
                total += parseInt(clients[i].bytesSent, 10) || 0;
            }
            return total;
        });

        self.runningServerProfiles = ko.pureComputed(function() {
            var profiles = self.installedProfiles();
            var running = [];
            for (var i = 0; i < profiles.length; i++) {
                if (profiles[i] && profiles[i].connected && profiles[i].is_server) {
                    running.push(profiles[i]);
                }
            }
            return running;
        });

        self.hasRunningServerProfile = ko.pureComputed(function() {
            return self.runningServerProfiles().length > 0;
        });

        self.activeServerHasCcd = ko.pureComputed(function() {
            var running = self.runningServerProfiles();
            for (var i = 0; i < running.length; i++) {
                if (running[i] && running[i].has_ccd) {
                    return true;
                }
            }
            return false;
        });

        // Parse OpenVPN config file
        self.parseConfig = function(content, fileName) {
            var lines = content.split('\n');
            var config = {
                mode: "p2p",
                device: "tun0",
                proto: "udp",
                remote: "",
                port: "1194",
                cipher: "AES-128-CBC",
                auth: "SHA1",
                tls: "",
                compress: "",
                filename: fileName
            };

            var directives = [];
            var embedded = [];
            var notes = [];

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                
                // Skip comments and empty lines
                if (!line || line[0] === '#' || line[0] === ';') continue;

                var parts = line.split(/\s+/);
                var keyword = parts[0];

                switch(keyword) {
                    case 'mode':
                        config.mode = parts[1] || config.mode;
                        break;
                    case 'dev':
                    case 'dev-type':
                        config.device = parts[1] || config.device;
                        break;
                    case 'proto':
                        config.proto = parts[1] || config.proto;
                        break;
                    case 'remote':
                        if (parts.length > 1) config.remote = parts[1];
                        if (parts.length > 2) config.port = parts[2];
                        break;
                    case 'cipher':
                        config.cipher = parts[1] || config.cipher;
                        break;
                    case 'auth':
                        config.auth = parts[1] || config.auth;
                        break;
                    case 'tls-version-min':
                    case 'tls-version-max':
                        if (parts[1]) config.tls = (config.tls || "") + parts[0] + "=" + parts[1] + " ";
                        break;
                    case 'comp-lzo':
                        config.compress = "LZO";
                        notes.push("comp-lzo is deprecated; consider using --compress LZ4");
                        break;
                    case 'compress':
                        if (parts[1]) config.compress = parts[1];
                        break;
                    case '<ca>':
                    case '<cert>':
                    case '<key>':
                    case '<dh>':
                    case '<tls-crypt>':
                    case '<tls-auth>':
                        embedded.push(keyword.replace(/[<>]/g, ''));
                        break;
                    case 'data-ciphers':
                        directives.push(keyword + " " + (parts.slice(1).join(" ") || ""));
                        notes.push("data-ciphers directive present; verify server compatibility");
                        break;
                    case 'verify-x509-name':
                    case 'ecdh-curve':
                    case 'dh':
                    case 'key-direction':
                    case 'keepalive':
                    case 'persist-key':
                    case 'persist-tun':
                    case 'nobind':
                    case 'user':
                    case 'group':
                    case 'daemon':
                        directives.push(keyword + (parts.length > 1 ? " " + parts.slice(1).join(" ") : ""));
                        break;
                }
            }

            self.detectedDirectives(directives);
            self.embeddedBlocks(embedded);
            self.compatibilityNotes(notes);
            self.rawConfig(content);
            self.parsedConfig(config);

            return config;
        };

        // Subscribe to file changes
        self.cfgdata.file.subscribe(function(file) {
            if (!file) return;

            var reader = new FileReader();
            reader.onload = function(e) {
                try {
                    var content = e.target.result;
                    if (content.length === 0) {
                        GauWeb.utils.showAlert("File is empty");
                        return;
                    }
                    self.parseConfig(content, file.name);
                    self.installStatus("");
                } catch(err) {
                    GauWeb.utils.showAlert("Error parsing file: " + err.message);
                }
            };
            reader.onerror = function() {
                GauWeb.utils.showAlert("Error reading file");
            };
            reader.readAsText(file);
        });

        // Install profile to device
        self.installProfile = function() {
            if (!self.cfgdata.file()) {
                GauWeb.notify("No file selected");
                return;
            }

            self.isInstalling(true);
            self.installStatus("");

            GauWeb.utils.fileUpload("/cgi-bin/ovpnimport.cgi", {
                query: "install",
                file: self.cfgdata.file()
            }, function(response) {
                self.isInstalling(false);

                if (!response || typeof response !== "object" || response.error || !response.filename) {
                    var failMessage = "Installation failed";
                    if (response && typeof response === "object" && response.message) {
                        failMessage = response.message;
                    } else if (typeof response === "string" && response.length > 0) {
                        failMessage = "Unexpected server response (not JSON).";
                    } else if (!response) {
                        failMessage = "No response from device";
                    }
                    self.installStatus(failMessage);
                    self.installSuccess(false);
                } else {
                    self.installStatus(response.message || ("Profile '" + response.filename + "' installed successfully"));
                    self.installSuccess(true);
                    self.cfgdata.clear();
                    self.parsedConfig(null);
                    self.rawConfig("");
                    self.loadInstalledProfiles();
                }
            });
        };

        // Load list of installed profiles
        self.loadInstalledProfiles = function() {
            $.ajax({
                url: "/cgi-bin/ovpnimport.cgi",
                type: "POST",
                data: { query: "list" },
                dataType: "json",
                success: function(response) {
                    if (!response.error && response.data) {
                        self.installedProfiles(response.data);
                    }
                },
                error: function() {
                    GauWeb.utils.showAlert("Error loading profile list");
                }
            });
        };

        self.profileAction = function(profile, action) {
            if (!profile || !profile.filename) {
                return;
            }

            self.busyProfile(profile.filename + ":" + action);

            $.ajax({
                url: "/cgi-bin/ovpnimport.cgi",
                type: "POST",
                data: {
                    query: action,
                    profile: profile.filename
                },
                dataType: "json",
                success: function(response) {
                    self.busyProfile("");
                    if (response && !response.error) {
                        self.installSuccess(true);
                        self.installStatus(response.message || ("Profile " + action + " complete"));
                    } else {
                        self.installSuccess(false);
                        self.installStatus(response ? (response.message || "Action failed") : "No response from device");
                    }
                    self.loadInstalledProfiles();
                },
                error: function() {
                    self.busyProfile("");
                    self.installSuccess(false);
                    self.installStatus("Error sending " + action + " request");
                }
            });
        };

        self.connectProfile = function(profile) {
            self.profileAction(profile, "connect");
        };

        self.disconnectProfile = function(profile) {
            self.profileAction(profile, "disconnect");
        };

        self.deleteProfile = function(profile) {
            if (!profile || !profile.filename) {
                return;
            }

            if (!window.confirm("Delete profile '" + profile.filename + "'?")) {
                return;
            }

            self.profileAction(profile, "delete");
        };

        self.isProfileBusy = function(profile, action) {
            if (!profile || !profile.filename) {
                return false;
            }
            return self.busyProfile() === (profile.filename + ":" + action);
        };

        self.runMgmtRequest = function(command, done) {
            self.isMgmtBusy(true);
            $.ajax({
                url: "/cgi-bin/ovpnimport.cgi",
                type: "POST",
                data: {
                    query: "mgmt_command",
                    host: self.mgmtHost(),
                    port: self.mgmtPort(),
                    password: self.mgmtPassword(),
                    command: command
                },
                dataType: "json",
                success: function(response) {
                    self.isMgmtBusy(false);
                    if (response && !response.error) {
                        self.mgmtSuccess(true);
                        self.mgmtStatus(response.message || "Management command completed");
                        self.mgmtConnected(true);
                        self.mgmtOutput(response.output || "");
                        self.updateClientsFromCommand(command, response.output || "");
                    } else {
                        self.mgmtSuccess(false);
                        self.mgmtStatus(response ? (response.message || "Management command failed") : "No response from device");
                        if (self.shouldMarkMgmtDisconnected(response)) {
                            self.mgmtConnected(false);
                        }
                        if (response && response.output) {
                            self.mgmtOutput(response.output);
                            self.updateClientsFromCommand(command, response.output);
                        }
                    }
                    if (done) {
                        done(response);
                    }
                },
                error: function() {
                    self.isMgmtBusy(false);
                    self.mgmtSuccess(false);
                    self.mgmtConnected(false);
                    self.mgmtStatus("Error communicating with management endpoint");
                    if (done) {
                        done(null);
                    }
                }
            });
        };

        self.shouldMarkMgmtDisconnected = function(response) {
            if (!response || !response.message) {
                return true;
            }
            var msg = String(response.message).toLowerCase();
            return msg.indexOf("failed to connect") >= 0 ||
                   msg.indexOf("requires a password") >= 0 ||
                   msg.indexOf("password rejected") >= 0 ||
                   msg.indexOf("invalid management") >= 0;
        };

        self.parseStatusClients = function(raw) {
            var clients = [];
            if (!raw) {
                return clients;
            }

            var lines = String(raw).split(/\r?\n/);
            for (var i = 0; i < lines.length; i++) {
                var line = (lines[i] || "").trim();
                if (!line || line.indexOf("CLIENT_LIST") < 0) {
                    continue;
                }

                var csvMatch = line.match(/CLIENT_LIST\s*,\s*([^,]+),([^,]+),(\d+),(\d+),([^,]*),([^,]*),?([^,]*),?([^,]*),?([^,]*)/);
                if (csvMatch) {
                    clients.push({
                        commonName: csvMatch[1] || "",
                        realAddress: csvMatch[2] || "",
                        bytesReceived: csvMatch[3] || "0",
                        bytesSent: csvMatch[4] || "0",
                        connectedSince: csvMatch[5] || "",
                        virtualAddress: csvMatch[6] || "",
                        clientId: csvMatch[9] || csvMatch[2] || "",
                        username: csvMatch[8] || ""
                    });
                    continue;
                }

                // Older OpenVPN status format can be whitespace/tab-delimited.
                var wsMatch = line.match(/CLIENT_LIST\s+([^\s]+)\s+([^\s]+:\d+)\s+([^\s]+)\s+(\d+)\s+(\d+)\s+(.+)$/);
                if (!wsMatch) {
                    continue;
                }

                var connectedSince = wsMatch[6] || "";
                connectedSince = connectedSince.replace(/\s+\d+\s+\S+$/g, "").trim();

                clients.push({
                    commonName: wsMatch[1] || "",
                    realAddress: wsMatch[2] || "",
                    virtualAddress: wsMatch[3] || "",
                    bytesReceived: wsMatch[4] || "0",
                    bytesSent: wsMatch[5] || "0",
                    connectedSince: connectedSince,
                    clientId: wsMatch[2] || "",
                    username: ""
                });
            }

            return clients;
        };

        self.formatBytes = function(value) {
            var bytes = parseInt(value, 10) || 0;
            if (bytes >= 1024 * 1024 * 1024) {
                return (bytes / (1024 * 1024 * 1024)).toFixed(1) + " GB";
            }
            if (bytes >= 1024 * 1024) {
                return (bytes / (1024 * 1024)).toFixed(1) + " MB";
            }
            if (bytes >= 1024) {
                return (bytes / 1024).toFixed(1) + " KB";
            }
            return String(bytes) + " B";
        };

        self.updateClientsFromCommand = function(command, output) {
            var cmd = String(command || "").toLowerCase();
            if (cmd.indexOf("status") === 0) {
                self.mgmtClients(self.parseStatusClients(output));
            }
        };

        self.stopMgmtPolling = function() {
            if (mgmtPollTimer) {
                clearInterval(mgmtPollTimer);
                mgmtPollTimer = null;
            }
        };

        self.startMgmtPolling = function() {
            self.stopMgmtPolling();

            var seconds = parseInt(self.mgmtPollSeconds(), 10);
            if (isNaN(seconds) || seconds < 1) {
                seconds = 5;
                self.mgmtPollSeconds(String(seconds));
            }

            mgmtPollTimer = setInterval(function() {
                if (!self.mgmtConnected() || self.isMgmtBusy()) {
                    return;
                }
                self.runMgmtRequest("status 3");
            }, seconds * 1000);
        };

        self.applyMgmtPolling = function() {
            if (!self.mgmtPollingEnabled()) {
                self.stopMgmtPolling();
                self.mgmtStatus("Realtime polling disabled");
                self.mgmtSuccess(true);
                return;
            }

            if (!self.mgmtConnected()) {
                self.mgmtSuccess(false);
                self.mgmtStatus("Connect before enabling realtime polling");
                self.mgmtPollingEnabled(false);
                return;
            }

            self.startMgmtPolling();
            self.mgmtStatus("Realtime polling enabled");
            self.mgmtSuccess(true);
            self.runMgmtRequest("status 3");
        };

        self.killMgmtClient = function(client) {
            if (!client) {
                return;
            }

            var target = client.clientId || client.commonName;
            if (!target) {
                self.mgmtSuccess(false);
                self.mgmtStatus("Client target is missing");
                return;
            }

            self.busyMgmtClient(target);
            self.runMgmtRequest("kill " + target, function() {
                self.busyMgmtClient("");
                if (self.mgmtConnected()) {
                    self.runMgmtRequest("status 3");
                }
            });
        };

        self.isMgmtClientBusy = function(client) {
            if (!client) {
                return false;
            }
            var target = client.clientId || client.commonName;
            return !!target && self.busyMgmtClient() === target;
        };

        self.hasRunningServerProfile.subscribe(function(isRunning) {
            if (!isRunning) {
                self.stopMgmtPolling();
                self.mgmtConnected(false);
                self.mgmtClients([]);
                self.busyMgmtClient("");
                self.mgmtStatus("No running server profile; management controls hidden");
                self.mgmtSuccess(true);
                self.ccdStatus("");
            }
        });

        self.connectManagement = function() {
            if (!self.hasRunningServerProfile()) {
                self.mgmtSuccess(false);
                self.mgmtStatus("Connect and run a server profile first");
                return;
            }
            self.runMgmtRequest("version", function(response) {
                if (response && !response.error) {
                    self.runMgmtRequest("status 3");
                    if (self.mgmtPollingEnabled()) {
                        self.startMgmtPolling();
                    }
                }
            });
        };

        self.disconnectManagement = function() {
            self.stopMgmtPolling();
            self.mgmtConnected(false);
            self.mgmtStatus("Disconnected from management interface");
            self.mgmtSuccess(true);
            self.mgmtClients([]);
        };

        self.runManagementCommand = function(cmd) {
            if (!self.hasRunningServerProfile()) {
                self.mgmtSuccess(false);
                self.mgmtStatus("Connect and run a server profile first");
                return;
            }

            if (!self.mgmtConnected()) {
                self.mgmtSuccess(false);
                self.mgmtStatus("Connect to management interface first");
                return;
            }

            var command = cmd || self.mgmtCommand();
            if (!command || !String(command).trim()) {
                self.mgmtSuccess(false);
                self.mgmtStatus("Enter a management command");
                return;
            }

            self.runMgmtRequest(command);
        };

        self.refreshMgmtClients = function() {
            self.runManagementCommand("status 3");
        };

        self.uploadCcdFile = function() {
            if (!self.hasRunningServerProfile()) {
                self.ccdSuccess(false);
                self.ccdStatus("Run a server profile before uploading CCD files");
                return;
            }

            if (!self.activeServerHasCcd()) {
                self.ccdSuccess(false);
                self.ccdStatus("Active server profile does not include client-config-dir ccd");
                return;
            }

            if (!self.ccdFileData.file()) {
                self.ccdSuccess(false);
                self.ccdStatus("No CCD file selected");
                return;
            }

            self.isCcdUploading(true);
            self.ccdStatus("");

            GauWeb.utils.fileUpload("/cgi-bin/ovpnimport.cgi", {
                query: "ccd_upload",
                file: self.ccdFileData.file()
            }, function(response) {
                self.isCcdUploading(false);
                if (response && !response.error) {
                    self.ccdSuccess(true);
                    self.ccdStatus(response.message || "CCD file uploaded");
                    self.ccdFileData.clear();
                } else {
                    self.ccdSuccess(false);
                    self.ccdStatus(response ? (response.message || "CCD upload failed") : "No response from device");
                }
            });
        };

        // Initialize
        self.loadInstalledProfiles();
    }

    return new OvpnImportModel();
});
