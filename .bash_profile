# Copy this file to your user home directory.

# uncomment for windows
#declare -rx XDG_CONFIG_HOME="$(cygpath "${XDG_CONFIG_HOME:-"${HOME}/.config"}")"
#declare -rx  XDG_CACHE_HOME="$(cygpath  "${XDG_CACHE_HOME:-"${HOME}/.cache"}")"
#declare -rx   XDG_DATA_HOME="$(cygpath   "${XDG_DATA_HOME:-"${HOME}/.local/share"}")"

# This should be useful on windows in `~/.bash_logout`:
# if [[ "$SHLVL" = 1 ]]
# then
#     taskkill //F //T //IM "ssh-agent.exe"
#     taskkill //F //T //IM "gpg-agent.exe"
# fi


#[[ -f "${XDG_CONFIG_HOME}/bash/main.sh"  ]] && source "${XDG_CONFIG_HOME}/bash/main.sh"

if [ "$TERM" = "linux" ]; then
    echo -en "\e]P000181E" #black
    echo -en "\e]P1DC322F" #darkred
    echo -en "\e]P2859900" #darkgreen
    echo -en "\e]P3B58900" #brown
    echo -en "\e]P4268BD2" #darkblue
    echo -en "\e]P5D33682" #darkmagenta
    echo -en "\e]P62AA198" #darkcyan
    echo -en "\e]P7EEE8D5" #lightgrey
    echo -en "\e]P8486870" #darkgrey
    echo -en "\e]P9CB4B16" #red
    echo -en "\e]PA98E34D" #green
    echo -en "\e]PBFFD75F" #yellow
    echo -en "\e]PC7373C9" #blue
    echo -en "\e]PD6C71C4" #magenta
    echo -en "\e]PE44C9C9" #cyan
    echo -en "\e]PFFDF6E3" #white
    clear #for background artifacting
fi
#gsettings set org.gnome.desktop.input-sources xkb-options "['caps:ctrl_modifier', 'lv3:ralt_alt']"
