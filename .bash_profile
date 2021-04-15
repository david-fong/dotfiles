# Copy this file to your user home directory.

declare -rx XDG_CONFIG_HOME="$(cygpath "${XDG_CONFIG_HOME:-"${HOME}/.config"}")"
declare -rx  XDG_CACHE_HOME="$(cygpath  "${XDG_CACHE_HOME:-"${HOME}/.cache"}")"
declare -rx   XDG_DATA_HOME="$(cygpath   "${XDG_DATA_HOME:-"${HOME}/.local/share"}")"
[[ -f "${XDG_CONFIG_HOME}/bash/main.sh"  ]] && source "${XDG_CONFIG_HOME}/bash/main.sh"

# This should be useful on windows in `~/.bash_logout`:
# if [[ "$SHLVL" = 1 ]]
# then
#     taskkill //F //T //IM "ssh-agent.exe"
#     taskkill //F //T //IM "gpg-agent.exe"
# fi
