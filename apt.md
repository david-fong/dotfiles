<https://apt.kitware.com/>
<https://mpv.io/installation/> (`deb https://apt.fruit.je/ubuntu oracular mpv`)
`add-apt-repository ppa:git-core/ppa`
`add-apt-repository ppa:linrunner/tlp`
<https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64>

## network privacy/security

`sudo systemctl enable ufw`
  block IP ranges: https://askubuntu.com/q/851785

<https://github.com/StevenBlack/hosts> (local DNS rejections)
  /etc/hosts

<https://one.one.one.one/family/> (outgoing DNS resolve/reject over TLS)
<https://developers.cloudflare.com/1.1.1.1/setup/linux/>
  <https://man.archlinux.org/man/resolved.conf.5>
  /etc/systemd/resolve.conf.d/main.conf: DNS= FallbackDNS=... DNSOverTLS=yes
    can copy file :/etc/systemd/resolved.conf.d/main.conf
    check with `resolvectl status`
  settings -> wifi -> each wifi network -> disable automatic DNS for ipv4 and ipv6
  sudo systemctl restart systemd-resolved
  <https://developers.cloudflare.com/1.1.1.1/check/>
  <https://developers.cloudflare.com/1.1.1.1/setup/#test-1111-for-families>

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

uBlockOrigin

<https://github.com/david-fong/david-fong.github.io/tree/main/browser-exts/header-editor>

## browser policy config

about:policy
/etc/brave/policies/managed/GroupPolicy.json
<https://support.brave.app/hc/en-us/articles/360039248271-Group-Policy#h_01HE8CWCDWF5SNASMCXTTQYZB5>
<https://chromeenterprise.google/intl/en_ca/policies>

## system packages

```
google-chrome-stable
dconf-editor
gnome-browser-connector
xbacklight xserver-xorg-video-intel
tlp tlp-rdw
pavucontrol
fonts-inconsolata
#wireguard
natpmpc # for vpn
zfsutils-linux rclone p7zip-full

tree nnn vim git git-lfs tig ripgrep jq reuse net-tools whois sqlite3 sqlitebrowser

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

<https://help.ubuntu.com/community/EnvironmentVariables#Persistent_environment_variables>

- [](https://askubuntu.com/questions/147462/how-can-i-change-the-tty-colors)

## keyboard

fun fact- chord `ctrl+shift+u, <unicode hex>` to enter unicode

- [](https://askubuntu.com/questions/1025765/how-to-map-alt-hjkl-keys-to-arrow-keys)
- [](https://askubuntu.com/a/257497)

<https://github.com/xkbcommon/libxkbcommon/blob/master/doc/keymap-text-format-v1-v2.md>
<https://xkbcommon.org/doc/current/user-configuration.html#compatibility>
<https://github.com/xkbcommon/libxkbcommon/blob/master/src/ks_tables.h>
- [](https://medium.com/@damko/a-simple-humble-but-comprehensive-guide-to-xkb-for-linux-6f1ad5e13450)
<https://wiki.archlinux.org/title/X_keyboard_extension>
<https://who-t.blogspot.com/2020/09/user-specific-xkb-configuration-putting.html>
  https://who-t.blogspot.com/2020/02/user-specific-xkb-configuration-part-1.html
  https://who-t.blogspot.com/2020/07/user-specific-xkb-configuration-part-2.html
  https://who-t.blogspot.com/2020/08/user-specific-xkb-configuration-part-3.html
https://github.com/xkbcommon/libxkbcommon/issues/18#issuecomment-72728366
https://github.com/xkbcommon/libxkbcommon/issues/145
TODO https://askubuntu.com/a/1216744/1624654 consider remapping alt key to something else and using that something else as the modifier?
https://docs.gtk.org/gtk3/property.Settings.gtk-enable-mnemonics.html annoyingly, this is deprecated.
<https://wiki.archlinux.org/title/X_keyboard_extension#Caps_hjkl_as_vimlike_arrow_keys>
(outdated): https://help.ubuntu.com/community/Custom%20keyboard%20layout%20definitions

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

edit `/etc/bashrc` and enable the bash-completions things

```
ln -sT /snap/code/current/usr/share/code/resources/completions/bash/code ~/.local/share/bash-completion/completions/code
```

a command to list manually installed packages:
courtesy of https://askubuntu.com/a/492343
```
alias aptlistman='comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n "s/^Package: //p" | sort -u) | less'
```

## data

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
