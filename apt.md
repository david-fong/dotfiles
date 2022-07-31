
```
dconf-editor
gnome-shell-extension-dash-to-panel (no longer on apt. install from website)
xbacklight
xserver-xorg-video-intel
tlp tlp-rdw
fonts-inconsolata

vim git git-lfs tig ripgrep reuse

libboost-all-dev
libssl-dev
ocl-icd-opencl-dev
default-jdk maven

gimp
ffmpeg pavucontrol

build-essential
clang clang-tidy conan g++
ninja-build make
linux-tools-generic
```

snaps:
```
audacity
cmake
code
discord
flutter
gradle
intellij-idea-community
node
zoom-client
```

- [](https://help.ubuntu.com/stable/ubuntu-help/power-batterylife.html.en)

- [](https://askubuntu.com/questions/147462/how-can-i-change-the-tty-colors)

- [](https://askubuntu.com/questions/1025765/how-to-map-alt-hjkl-keys-to-arrow-keys)
- [](https://askubuntu.com/a/257497)
- [](https://medium.com/@damko/a-simple-humble-but-comprehensive-guide-to-xkb-for-linux-6f1ad5e13450)
<https://wiki.archlinux.org/title/X_keyboard_extension>

- [](https://askubuntu.com/questions/103249/how-to-increase-brightness-in-smaller-steps/1080149#1080149)

- [](https://askubuntu.com/questions/315625/how-to-disable-the-shortcut-ctrl-alt-arrow-in-gnome-3-8)
- [](https://unix.stackexchange.com/questions/260601/understanding-setting-up-different-input-methods)

- [](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)

- [](https://www.youtube.com/watch?v=KA6A3oeocHY&ab_channel=MentalOutlaw)
- [](https://github.com/StevenBlack/hosts)

edit `/etc/bashrc` and enable the bash-completions things


a command to list manually installed packages:
courtesy of https://askubuntu.com/a/492343
```
alias aptlistman='comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n "s/^Package: //p" | sort -u) | less'
```
