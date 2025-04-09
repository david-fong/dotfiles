https://apt.kitware.com/
https://mpv.io/installation/
add-apt-repository ppa:git-core/ppa (deb https://apt.fruit.je/ubuntu noble mpv)
https://code.visualstudio.com/download (.deb)

network privacy/security
sudo systemctl enable ufw
  block IP ranges: https://askubuntu.com/q/851785
https://github.com/StevenBlack/hosts (local DNS rejections)
  /etc/hosts
https://one.one.one.one/family/ (outgoing DNS resolve/reject over TLS)
https://developers.cloudflare.com/1.1.1.1/setup/linux/
  https://man.archlinux.org/man/resolved.conf.5
  /etc/systemd/resolve.conf: DNS= FallbackDNS=... DNSOverTLS=yes
    can copy file :/etc/systemd/resolved.conf.d/main.conf
  settings -> wifi -> each wifi network -> disable automatic DNS for ipv4 and ipv6
  sudo systemctl restart systemd-resolved
  https://developers.cloudflare.com/1.1.1.1/check/
  https://developers.cloudflare.com/1.1.1.1/setup/#test-1111-for-families
https://protonvpn.com (hide IP address)
  https://protonvpn.com/support/linux-openvpn#NetworkManager
  NOPE (network manager doesn't support autoconnect?) https://protonvpn.com/support/wireguard-linux#NetworkManager
    download with moderate NAT, NAT-PMP, and VPN accellerator. set netshield blocker to highest
  https://account.protonvpn.com/downloads#wireguard-configuration
  https://account.protonvpn.com/account-password#openvpn
  https://askubuntu.com/q/1033278 auto turn on vpn
  https://old.reddit.com/r/selfhosted/comments/1f6pu6q/comment/ll1y1r2 TODO
    or https://protonvpn.com/support/bittorrent-vpn
  OPTIONAL(speed) https://protonvpn.com/support/port-forwarding-manual-setup
    username+pmp+f2+nr
    https://protonvpn.com/support/port-forwarding
    https://protonvpn.com/blog/port-forwarding/
  https://protonvpn.com/support/advanced-kill-switch
uBlockOrigin
https://github.com/david-fong/david-fong.github.io/tree/main/browser-exts/header-editor

```
dconf-editor
gnome-browser-connector
xbacklight xserver-xorg-video-intel
tlp tlp-rdw
pavucontrol
fonts-inconsolata
natpmpc # for vpn

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
mold
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

- [](https://askubuntu.com/questions/1025765/how-to-map-alt-hjkl-keys-to-arrow-keys)
- [](https://askubuntu.com/a/257497)

- [](https://medium.com/@damko/a-simple-humble-but-comprehensive-guide-to-xkb-for-linux-6f1ad5e13450)
<https://wiki.archlinux.org/title/X_keyboard_extension>
https://who-t.blogspot.com/2020/02/user-specific-xkb-configuration-part-1.html
https://who-t.blogspot.com/2020/07/user-specific-xkb-configuration-part-2.html
https://who-t.blogspot.com/2020/08/user-specific-xkb-configuration-part-3.html
https://who-t.blogspot.com/2020/09/user-specific-xkb-configuration-putting.html
https://github.com/xkbcommon/libxkbcommon/issues/18#issuecomment-72728366
https://github.com/xkbcommon/libxkbcommon/issues/145
TODO https://askubuntu.com/a/1216744/1624654 consider remapping alt key to something else and using that something else as the modifier?
https://docs.gtk.org/gtk3/property.Settings.gtk-enable-mnemonics.html annoyingly, this is deprecated.

- [](https://askubuntu.com/questions/103249/how-to-increase-brightness-in-smaller-steps/1080149#1080149)

- [](https://askubuntu.com/questions/315625/how-to-disable-the-shortcut-ctrl-alt-arrow-in-gnome-3-8)
- [](https://unix.stackexchange.com/questions/260601/understanding-setting-up-different-input-methods)

- [](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
https://askubuntu.com/q/67758 disable bluetooth on startup
  /etc/bluetooth/main.conf AutoEnable=false
https://askubuntu.com/q/223018 vim is not remembering last position

- [](https://www.youtube.com/watch?v=KA6A3oeocHY&ab_channel=MentalOutlaw)

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

edit `/etc/bashrc` and enable the bash-completions things


a command to list manually installed packages:
courtesy of https://askubuntu.com/a/492343
```
alias aptlistman='comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n "s/^Package: //p" | sort -u) | less'
```

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

```
ln -sT /snap/code/current/usr/share/code/resources/completions/bash/code ~/.local/share/bash-completion/completions/code
```

adblock allowlist:
```
@@stackexchange.com$document
@@stackoverflow.com$document
@@||i.stack.imgur.com/*^$document
```
