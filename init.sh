cp ~/.config/bash/profile ~/.profile
[ -f ~/.bashrc ] && mv ~/.bashrc ~/.bashrc~
[ -f ~/.bash_profile ] && mv ~/.bash_profile ~/.bash_profile~

mkdir -p ~/c
mkdir -p ~/c/m

if [ -x /usr/bin/gsettings ]; then
	gsettings set org.gnome.desktop.input-sources xkb-options "['ctrl:nocaps']"
	gsettings set org.gnome.desktop.wm.keybindings panel-run-dialog "['<Super>r']"
	gsettings set org.gnome.desktop.wm.keybindings switch-windows "['<Alt>Tab', '<Mod3>XF86ApplicationRight']"
	gsettings set org.gnome.desktop.wm.keybindings switch-windows-backward "['<Shift><Alt>Tab', '<Shift><Mod3>XF86ApplicationLeft']"
	gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-left "['<Super>Page_Up', '<Super><Alt>Left', '<Control><Alt>Left', '<Mod3>Prev_Virtual_Screen']"
	gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-right "['<Super>Page_Down', '<Super><Alt>Right', '<Control><Alt>Right', '<Mod3>Next_Virtual_Screen']"
	gsettings set org.gnome.mutter.wayland.keybindings switch-to-session-1 "['<Primary><Alt>F1', '<mod3>XF86Switch_VT_1']"
	gsettings set org.gnome.mutter.wayland.keybindings switch-to-session-2 "['<Primary><Alt>F2', '<mod3>XF86Switch_VT_2']"
	gsettings set org.gnome.mutter.wayland.keybindings switch-to-session-3 "['<Primary><Alt>F3', '<mod3>XF86Switch_VT_3']"
	gsettings set org.gnome.mutter.wayland.keybindings switch-to-session-4 "['<Primary><Alt>F4', '<mod3>XF86Switch_VT_4']"
fi

[ -x dconf ] && [ -x /usr/bin/gnome-terminal ] && dconf load /org/gnome/terminal/ < ~/.config/gnome-terminal.dump

# https://superuser.com/a/215506
mkdir -p -m700 ~/.ssh
[ -f ~/.ssh/config ] || echo 'AddKeysToAgent=yes' > ~/.ssh/config
chmod 600 ~/.ssh/*
chmod 644 ~/.ssh/*.pub
[ -f ~/.ssh/authorized_keys ] && chmod 644 ~/.ssh/authorized_keys
#chmod -R go-rwx ~/Documents/secret*

# https://support.brave.app/hc/en-us/articles/360039248271-Group-Policy#h_01HE8CWCDWF5SNASMCXTTQYZB5
# https://chromeenterprise.google/intl/en_ca/policies
[ -d /etc ] && mkdir -p /etc/brave/policies/managed/
[ -d /etc ] && cp ~/.config/etc/brave/policies/managed/GroupPolicy.json /etc/brave/policies/managed/

# https://code.visualstudio.com/docs/setup/enterprise#_json-policies-on-linux
[ -d /etc ] && mkdir -p /etc/vscode/
[ -d /etc ] && cp ~/.config/etc/vscode/policy.json /etc/vscode/policy.json
