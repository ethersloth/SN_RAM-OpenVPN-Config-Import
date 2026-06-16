# SN RAM – OpenVPN Config Import

A web-based OpenVPN profile manager for **Red Lion RAM/SN series** devices (RAM-9931 and similar). Delivered as a standard SN SDK package (`snupdate`) that adds an **Extensions → OpenVPN Import** page to the existing device web UI.

---

## Features

| Feature | Details |
|---|---|
| Profile Upload | Drag-and-drop `.ovpn` or `.conf` files; parses and displays a summary before install |
| Profile Install | Writes to `/etc/openvpn/`, restarts the OpenVPN service automatically |
| Profile Management | Connect / Disconnect / Delete any installed profile from the UI |
| Server/Client Detection | Automatically detects `server`, `mode server`, or `tls-server` directives |
| Management Port Panel | Available only when a **server** profile is running |
| Management Commands | `version`, `state`, `status 3`, `log 50`, or any custom command |
| Realtime Polling | Configurable polling interval to keep status fresh |
| Connected Client List | Parsed from `status 3`; shows CN, real address, virtual IP, RX/TX, Kill action |
| CCD Upload | Upload per-client config files to `/etc/openvpn/ccd` (auto-created) when `client-config-dir ccd` is present in the server config |
| Detailed Syslog | All actions log success/failure reason via `logger` for `slog` / `tail /var/log/messages` |

---

## Requirements

- Red Lion RAM/SN device with `snupdate` v1.x
- OpenVPN binary at `/sbin/openvpn` (standard on supported firmware)
- Device firmware with lighttpd + Perl CGI support (standard JBM/GauWeb stack)

---

## Install

### Via Device Web UI
1. Download `OpenVPN_Import.zip` from the [latest release](../../releases/latest).
2. On the device web UI go to **Admin → Package Installation**.
3. Upload `OpenVPN_Import.zip` and click **Upload**.

### Via SSH
```bash
scp OpenVPN_Import.zip rlcuser@<device-ip>:/tmp/
ssh -t -p 2022 rlcuser@<device-ip> "su -c 'snupdate /tmp/OpenVPN_Import.zip'"
```

Then navigate to **Extensions → OpenVPN Import**.

---

## Usage

### Uploading a Profile
1. Drag and drop an `.ovpn` or `.conf` file onto the upload area (or click to browse).
2. Review the parsed summary (mode, proto, remote, cipher, embedded content).
3. Click **Install to Device**.

### Connecting / Disconnecting
- The **Installed Profiles** table shows all `.conf` files in `/etc/openvpn/`.
- Use **Connect** / **Disconnect** / **Delete** per profile.
- The **Mode** column shows `server` or `client` based on config directives.

### Management Port (Server Profiles Only)
The management panel appears automatically when a server profile is running.

1. Set **Host** (`127.0.0.1`) and **Port** (matches `management` directive in your server config, default `7505`).
2. Click **Connect** — the panel will run `version` then `status 3` automatically.
3. Use the quick buttons (**Status 3**, **State**, **Version**, **Log 50**) or type a custom management command.
4. Enable **Realtime Polling** with a configurable interval to keep the client list live.
5. Click **Kill** on any connected client row to drop that session.

### CCD File Upload
If the running server config contains `client-config-dir ccd`, a **CCD File Upload** section appears. Name your file after the client's Common Name and upload it — it will be placed in `/etc/openvpn/ccd/` (directory is auto-created if missing).

---

## Package Structure

```
OpenVPN_Import.zip
├── install.sh                                    # snupdate install script
└── home/httpd/jbmconfig/
    ├── html/pages/
    │   ├── ovpnimport.html                       # Page UI (Knockout templates)
    │   └── ovpnimport.js                         # Frontend view model
    └── cgi-bin/
        └── ovpnimport.cgi                        # Perl CGI backend
```

The `install.sh` also registers the page in `customTabs.txt` so it appears under Extensions.

---

## Building from Source

```bash
git clone https://github.com/ethersloth/SN_RAM-OpenVPN-Config-Import.git
cd SN_RAM-OpenVPN-Config-Import

# Verify CGI syntax
perl -c home/httpd/jbmconfig/cgi-bin/ovpnimport.cgi

# Build package (requires an install.sh and pkg_build tree — see SN_Dev workspace)
cd pkg_build
zip -r ../SN_RAM_Packages/OpenVPN_Import/OpenVPN_Import.zip install.sh home/
```

---

## Known Issues / Roadmap

- **Management client status list** — the telnet-based management socket transport on the stripped embedded Perl environment has timing issues that prevent `status 3` output from reliably populating the client table. A compiled C helper (or Busybox `nc` if available on target firmware) would be a clean fix.
- **No multi-profile server support** — management port settings apply globally; if multiple server profiles are running simultaneously, only the first is targeted.

---

## License

MIT
