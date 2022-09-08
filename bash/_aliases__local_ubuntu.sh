
alias proj='cd "$HOME/code/mine/okiidoku/cpp"'

# https://github.com/emscripten-core/emscripten/issues/4848#issuecomment-1097357775
#. "/home/david/code/tool/emsdk/emsdk_env.sh"
declare -x EMSDK="$HOME/code/tool/emsdk"
PATH+=":$EMSDK:$EMSDK/upstream/emscripten"

PATH+=":$HOME/.local/share/npm/bin"

alias aptlistman='comm -23 <(apt-mark showmanual | sort -u) <(gzip -dc /var/log/installer/initial-status.gz | sed -n "s/^Package: //p" | sort -u) | less'
