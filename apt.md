<https://apt.kitware.com/>
<https://mpv.io/installation/> (`deb https://apt.fruit.je/ubuntu oracular mpv`)
`add-apt-repository ppa:git-core/ppa`
`add-apt-repository ppa:linrunner/tlp`
`add-apt-repository ppa:tomtomtom/yt-dlp` # https://github.com/yt-dlp/yt-dlp/wiki/Installation#apt
<https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64>
<https://docs.conda.io/projects/conda/en/stable/user-guide/install/rpm-debian.html>

## network privacy/security

`sudo systemctl enable ufw`
  block IP ranges: https://askubuntu.com/q/851785

<https://github.com/StevenBlack/hosts> (local DNS rejections)
  /etc/hosts

https://dnsleaktest.com/
<https://one.one.one.one/family/> (outgoing DNS resolve/reject over TLS)
<https://developers.cloudflare.com/1.1.1.1/setup/linux/#systemd-resolved>
  <https://man.archlinux.org/man/resolved.conf.5>
  /etc/systemd/resolved.conf.d/main.conf: DNS= FallbackDNS=... DNSOverTLS=yes
    can copy file :/etc/systemd/resolved.conf.d/main.conf
    check with `resolvectl status`
      https://github.com/systemd/systemd/issues/17330
    edit with `sudoedit /etc/systemd/resolved.conf.d/main.conf && sudo systemctl restart systemd-resolved; resolvectl status`
    `sudo systemctl restart systemd-resolved; resolvectl status`
    `sudo systemd-analyze cat-config systemd/resolved.conf` to view all resolved.conf files together?
  https://wiki.gnome.org/Projects/NetworkManager/DNS
  <!-- settings -> wifi -> each wifi network -> disable automatic DNS for ipv4 and ipv6
    alternatively (same result, different UI :/), in network manager IPv4/IPv6 settings, my (possibly wrong) understanding is that Method: "Automatic (DHCP|VPN)" means it will handle DNS, but if you select "Automatic (DHCP|VPN), addresses only", it won't handle DNS. So I generally turn the DNS off, except for VPNs I trust that handle DNS.
    or alternatively, `nmcli con mod "$connectionName" ipv4.ignore-auto-dns yes` (and similar for ipv6) and then `sudo service NetworkManager restart` -->
  `man nm-system-settings.conf`
  ```
  nmcli con mod "$wifi" connection.dns-over-tls yes
  nmcli con mod "$wifi" ipv4.ignore-auto-dns yes
  nmcli con mod "$wifi" ipv6.ignore-auto-dns yes
  nmcli con mod "$wifi" ipv4.dns 1.1.1.2,1.0.0.2
  nmcli con mod "$wifi" ipv6.dns 2606:4700:4700::1112,2606:4700:4700::1002
  # doesn't actually enable dns over tls for protonvpn, but should be okay, since it's going through the vpn tunnel:
  nmcli con mod tun0  connection.dns-over-tls yes
  nmcli con mod "$vpn"  connection.dns-over-tls yes
  nmcli con mod "$vpn"  ipv4.dns-search '~'
  nmcli con mod "$vpn"  ipv6.dns-search '~'
  # now, be in total control for my search domains ('~' := everything). don't let any other connection have a say:
  nmcli con mod "$vpn"  ipv4.dns-priority '-1'
  nmcli con mod "$vpn"  ipv6.dns-priority '-1'
  sudo service NetworkManager restart
  ```
  <https://developers.cloudflare.com/1.1.1.1/check/>
    test by opening <https://one.one.one.one/help>
  <https://developers.cloudflare.com/1.1.1.1/setup/#test-1111-for-families>
    test by opening <https://malware.testcategory.com/>
[DNS over HTTPS is slightly better than ovre TLS for privacy](https://www.cloudflare.com/learning/dns/dns-over-tls/#:~:text=than%20physical%20connections.-,Which%20is%20better,-%2C%20DoT%20or%20DoH), but [systemd-resolved doesn't support it yet](https://github.com/systemd/systemd/issues/8639).
  > Like DoT, DoH ensures that attackers can't forge or alter DNS traffic. DoH traffic looks like other HTTPS traffic – e.g. normal user-driven interactions with websites and web apps – from a network administrator's perspective.

testing dnssec: https://wander.science/projects/dns/dnssec-resolver-test/
testing dns over tls: `\sudo tcpdump -ni wlp0s20f3 -p port 53 or port 853` and look for 853, and absence of 53.

https://protonvpn.com/what-is-my-ip-address
https://protonvpn.com (hide IP address)
  <https://protonvpn.com/support/linux-openvpn#NetworkManager>
  <https://protonvpn.com/support/wireguard-linux#NetworkManager>
    download with moderate NAT, NAT-PMP, and VPN accellerator. set netshield blocker to highest
    <https://account.protonvpn.com/downloads#wireguard-configuration>
    `sudo mv ~/Downloads/proton_CA-####.conf /etc/wireguard`
    `sudo nmcli connection import type wireguard file /etc/wireguard/proton_CA-####.conf`
    <https://wiki.debian.org/WireGuard#Step_2_-_Alternative_D_-_systemd_with_wg-quick>
    `sudo systemctl enable wg-quick@proton_CA-####.service`
    `sudo systemctl daemon-reload`
    `sudo systemctl start wg-quick@proton_CA-####`
    `sudo systemctl status wg-quick@proton_CA-####`
      <https://www.wireguard.com/quickstart/>
      <https://documentation.ubuntu.com/server/how-to/wireguard-vpn/common-tasks/>
  <https://account.protonvpn.com/account-password#openvpn>
  <https://askubuntu.com/q/1033278> auto turn on vpn
  <https://old.reddit.com/r/selfhosted/comments/1f6pu6q/comment/ll1y1r2> TODO (force transmission to go through VPN)
    or <https://protonvpn.com/support/bittorrent-vpn>
  OPTIONAL(speed) <https://protonvpn.com/support/port-forwarding-manual-setup>
    `<username>+pmp+f2+nr`
    <https://protonvpn.com/support/port-forwarding>
    <https://protonvpn.com/blog/port-forwarding/>
  <https://protonvpn.com/support/advanced-kill-switch>
  <https://proton.me/support/installing-bridge-linux-deb-file>
  <https://proton.me/support/verifying-bridge-package>
  `ip route` (lower "metric" means higher priority)

uBlockOrigin

<https://github.com/david-fong/david-fong.github.io/tree/main/browser-exts/header-editor>

## browser policy config

about:policy
/etc/brave/policies/managed/GroupPolicy.json
<https://support.brave.app/hc/en-us/articles/360039248271-Group-Policy#h_01HE8CWCDWF5SNASMCXTTQYZB5>
<https://chromeenterprise.google/intl/en_ca/policies>
in settings, set webrtc IP handling policy to "Default public Interface only" https://support.brave.app/hc/en-us/articles/360017989132-How-do-I-change-my-Privacy-Settings#webrtc

## system packages

```
google-chrome-stable brave brave-keyring # is the keyring needed?
dconf-editor
gnome-browser-connector
tlp tlp-rdw
pavucontrol
fonts-inconsolata
#wireguard
#network-manager-openconnect-gnome # open substitute for cisco anyconnect. using to connect to ubc vpn.
natpmpc # for vpn
zfsutils-linux rclone p7zip-full

tree nnn lf vim git git-lfs tig ripgrep jq reuse net-tools whois sqlite3 sqlitebrowser

libboost-all-dev
libssl-dev
# ocl-icd-opencl-dev
# default-jdk

gimp imagemagick
exif ffmpeg
yt-dlp mpv
audacity

g++ clang
clang-tidy doxygen
lld mold
ninja-build make
cmake
conan
linux-tools-generic
python3-typeshed # installed for GDB API types

# for ubc 2026 work, installed to run playwright:
libicu76 libxml2-16 libavif16 libmanette-0.2-0
docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin # for docker
libreoffice-base libreoffice-sdbc-postgresql # for postgres
```

snaps:
```
#discord
#flutter
#gradle
#intellij-idea-community
node
zoom-client
```

gnome extensions:
dash-to-panel@jderose9.github.com

custom keyboard shortcuts:
`xbacklight -dec 1 -time 333 -steps 2` for shift+MonBrightnessDown
`xbacklight -inc 1 -time 333 -steps 2` for shift+MonBrightnessUp

dump gnome-terminal settings:
dconf dump /org/gnome/terminal/ > ~/.config/gnome-terminal.dump
dconf load /org/gnome/terminal/ < ~/.config/gnome-terminal.dump

nmcli connection modify docker0 ipv4.never-default yes
nmcli connection modify docker0 ipv6.never-default yes

<https://help.ubuntu.com/community/EnvironmentVariables#Persistent_environment_variables>

- [](https://askubuntu.com/questions/147462/how-can-i-change-the-tty-colors)

ptyxis themes: wombat, peppermint, vibrant ink, argonaut, one half black, hardcore, website

## keyboard

fun fact- chord `ctrl+shift+u, <unicode hex>` to enter unicode

- [](https://askubuntu.com/questions/1025765/how-to-map-alt-hjkl-keys-to-arrow-keys)
- [](https://askubuntu.com/a/257497)

<https://xkbcommon.org/doc/current/keymap-text-format-v1-v2.html>
  (source: <https://github.com/xkbcommon/libxkbcommon/blob/master/doc/keymap-text-format-v1-v2.md>)
<https://xkbcommon.org/doc/current/user-configuration.html#compatibility>
<https://github.com/xkbcommon/libxkbcommon/blob/master/src/ks_tables.h>
  https://www.x.org/releases/current/doc/kbproto/xkbproto.html
<https://wiki.archlinux.org/title/X_keyboard_extension>
xkb tutorials:
  <https://who-t.blogspot.com/2020/09/user-specific-xkb-configuration-putting.html>
    https://who-t.blogspot.com/2020/02/user-specific-xkb-configuration-part-1.html
    https://who-t.blogspot.com/2020/07/user-specific-xkb-configuration-part-2.html
    https://who-t.blogspot.com/2020/08/user-specific-xkb-configuration-part-3.html
  (a bit outdated) [An Unreliable Guide to XKB Configuration](https://www.charvolant.org/doug/xkb/html/index.html)
  (a bit outdated and maybe not the best guide) https://medium.com/@damko/a-simple-humble-but-comprehensive-guide-to-xkb-for-linux-6f1ad5e13450
  (outdated): https://help.ubuntu.com/community/Custom%20keyboard%20layout%20definitions
https://github.com/xkbcommon/libxkbcommon/issues/18#issuecomment-72728366
https://github.com/xkbcommon/libxkbcommon/issues/145

https://wiki.archlinux.org/title/Xorg/Keyboard_configuration#Using_localectl
https://www.x.org/releases/X11R7.5/doc/input/XKB-Config.html
https://www.charvolant.org/doug/xkb/html/node4.html#SECTION00041000000000000000

https://bugs.freedesktop.org/show_bug.cgi?id=78661#c6
https://github.com/xkbcommon/libxkbcommon/issues/145
  https://github.com/xkbcommon/libxkbcommon/issues/18

https://w3c.github.io/uievents/tools/key-event-viewer.html

- [](https://askubuntu.com/questions/103249/how-to-increase-brightness-in-smaller-steps/1080149#1080149)

- [](https://askubuntu.com/questions/315625/how-to-disable-the-shortcut-ctrl-alt-arrow-in-gnome-3-8)
- [](https://unix.stackexchange.com/questions/260601/understanding-setting-up-different-input-methods)

- [](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
https://askubuntu.com/q/67758 disable bluetooth on startup
  /etc/bluetooth/main.conf AutoEnable=false
https://askubuntu.com/q/223018 vim is not remembering last position

- [](https://www.youtube.com/watch?v=KA6A3oeocHY&ab_channel=MentalOutlaw)

## more browser config

chrome://flags/#global-media-controls-cast-start-stop  disabled
chrome://flags/#allow-all-sites-to-initiate-mirroring  disabled
chrome://flags/#tab-organization                       disabled
chrome://flags/#multi-tab-organization                 disabled
chrome://flags/#tab-reorganization                     disabled
chrome://flags/#tab-reorganization-divider             disabled
chrome://flags/#scrollable-tabstrip                    disabled
https://www.usa.canon.com/support/p/imageclass-mf4570dw (it manually installed libjpeg62, and some libcups/cups stuff libcupsimage2t64)

https://stackoverflow.com/q/70782793/11107541 Is there a way to suppress sec-ua* headers in Chrome?
https://superuser.com/a/1497461/1749748 Is it possible to disable the HTTP referer header being passed by browsers?
https://askubuntu.com/q/293546/1624654 How to launch google-chrome with custom parameters by default?
https://developer-old.gnome.org/desktop-entry-spec/
xdg-desktop-menu forceupdate
 --enable-features=ReduceUserAgent --no-referrers --disable-domain-reliability --metrics-recording-only --no-pings
https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
https://peter.sh/experiments/chromium-command-line-switches/
https://chromium.googlesource.com/chromium/src/+/361ea625a796df11fb159a837a8cd3d7265873d7 `enable_referrers` preference
https://superuser.com/a/1840964/1749748
gsettings set org.gnome.desktop.wm.preferences focus-new-windows 'strict' # eh. I tried it and it's just too annoying.

chrome://settings/syncSetup -> "Other Google Services"
- Automatically sends usage statistics and crash reports to Google: off
- Send URLs of pages that you visit to Google: off
- To fix spelling errors, Chrome sends the text that you type in the browser to Google: off
- When you type in the address bar or search box, Chrome sends what you type to your default search engine to get better suggestions. This is off in Incognito: off
chrome://settings/security
- Always use secure connections: on
- Use secure DNS: on
chrome://settings/system
- Continue running background apps when Chrome is closed: off

## power config

- [](https://help.ubuntu.com/stable/ubuntu-help/power-batterylife.html.en)
https://askubuntu.com/q/1014187 Thinkpad Battery drops at 40%
https://linrunner.de/tlp/usage/tlp.html#perform-a-battery-recalibration-while-on-ac-power
https://linrunner.de/tlp/installation/ubuntu.html
in /etc/tlp.conf
```
START_CHARGE_THRESH_BAT0=36
STOP_CHARGE_THRESH_BAT0=41
```
https://askubuntu.com/q/1405846/1624654 set ubuntu low power value

## completions

edit `/etc/bash.bashrc` and enable the bash-completions things

a command to list manually installed packages:
courtesy of https://askubuntu.com/a/492343
```
alias aptlistman='comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n "s/^Package: //p" | sort -u) | less'
```

## data

```
/etc/systemd/journald.conf
# https://askubuntu.com/a/1276078
SystemMaxUse=128M
```

<https://old.reddit.com/r/DataHoarder/comments/6qf716/a_quick_datahoarder_faq/>
<https://old.reddit.com/r/DataHoarder/wiki/hardware#wiki_hard_drives>
  avoid SMR (Shingled Magnetic Recording) in RAID/ZFS setups. prefer CMR (Conventional Magnetic Recording)
<https://old.reddit.com/r/DataHoarder/wiki/zfs>
<https://old.reddit.com/r/DataHoarder/wiki/backups>
<https://www.andyibanez.com/posts/rclone-basics-encryption/>
<https://www.bestbuy.ca/en-ca/category/network-attached-storage-nas/29582>
<https://www.bestbuy.ca/en-ca/category/external-hard-drives/20237>
  <https://www.bestbuy.ca/en-ca/product/wd-wdbdff0020bbk-wesn-2-tb-hard-drive-external-portable/13504497>

## laptop

<https://psref.lenovo.com/syspool/Sys/PDF/ThinkPad/ThinkPad_T490/ThinkPad_T490_Spec.PDF>

thinkpad t490 repair videos
<https://pcsupport.lenovo.com/ca/en/products/laptops-and-netbooks/thinkpad-t-series-laptops/thinkpad-t490-type-20n2-20n3/selfrepair/removalsreplacements>

https://www.lenovo.com/ca/en/glossary/differences-between-mobile-workstation-and-laptop/
  "mobile workstation" just means more beefy/powerful than "laptop"
I want a thinkpad P or T series. P is "mobile workstation"s. I probably want 16 gigs of RAM with slot for expansion, and 256 gigs of SSD. pick one that allows not buying windows license (i.e. linux).
