#!/bin/bash
# Some ideas taken from https://github.com/mrzool/bash-sensible/blob/master/sensible.bash

#[[ "$MINGW64_HOME"     ]] &&      MINGW64_HOME="$(cygpath "$MINGW64_HOME")"
#[[ "$JAVA_HOME"        ]] &&         JAVA_HOME="$(cygpath "$JAVA_HOME")"
#[[ "$GRADLE_HOME"      ]] &&       GRADLE_HOME="$(cygpath "$GRADLE_HOME")"
#[[ "$MONGODB_HOME"     ]] &&      MONGODB_HOME="$(cygpath "$MONGODB_HOME")"

source "${XDG_CONFIG_HOME}/bash/xdg_compat.sh"

# exit if not running interactively:
[[ "$-" =~ "i" ]] || return

# disable sending and receiving XON/XOFF
stty -ixoff -ixon

tabs -3

# set codepage (on windows) to UTF-8
# https://docs.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
# mintty no longer needs this, but the new windows terminal does.
# https://github.com/msys2/msys2-runtime/pull/15
#chcp.com 65001 2> /dev/null

shopt -s checkhash globstar extglob checkwinsize
export FUNCNEST=100


shopt -s histappend cmdhist
declare -a histignore=(
	'sudo\ *' 'rm\ -rf'
	'fg' 'fg\ *' 'hist' 'history' 'hash' 'bind' 'clear'
	'config' 'inputrc' 'bashrc' 'als' 'alsl' 'vimrc' 'gitconfig' 'tigrc'
	'cd\ \.\.*' 'ls' 'lsa' 'lsen\ *' 'nnn' 'n'
	'todo'
	#'./build*' './main' 'npm\ run\ start'
	'tig' 'git\ status' 'git\ s' 'g\ s' 's' 'git\ a\ *' 'g\ a\ *' 'git\ br' 'g\ br' 'git\ diff' 'git\ d' 'g\ d' 'git\ dc' 'g\ dc' 'gti\ *'
)
HISTIGNORE=
for pattern in "${histignore[@]}"; do
	HISTIGNORE+="$pattern"':'
done
unset histignore
HISTCONTROL=ignoredups:ignorespace:erasedups
HISTSIZE=2048
HISTFILESIZE=4096
HISTTIMEFORMAT='%F %T '
#PROMPT_COMMAND='history -a' # Record each line as it gets issued


export NODE_ENV='development'
#PATH+=":$(cygpath "${APPDATA}")/npm"
[[ -f "${XDG_CONFIG_HOME}/npm/completion" ]] && . "${XDG_CONFIG_HOME}/npm/completion"

export EDITOR='vim'
# CSCOPE_EDITOR='view'


[[ -f "${XDG_CONFIG_HOME}/bash/aliases.sh"        ]] && . "${XDG_CONFIG_HOME}/bash/aliases.sh"
[[ -f "${XDG_CONFIG_HOME}/bash/aliases__local.sh" ]] && . "${XDG_CONFIG_HOME}/bash/aliases__local.sh"
alias   inputrc='"$EDITOR" "${XDG_CONFIG_HOME}/readline/inputrc"'
alias    bashrc='"$EDITOR" "${XDG_CONFIG_HOME}/bash/main.sh"'
alias       als='"$EDITOR" "${XDG_CONFIG_HOME}/bash/aliases.sh"'
alias      alsl='"$EDITOR" "${XDG_CONFIG_HOME}/bash/aliases__local.sh"'
alias     vimrc='"$EDITOR" "${XDG_CONFIG_HOME}/vim/main.vim"'
alias gitconfig='"$EDITOR" "${XDG_CONFIG_HOME}/git/config"'
alias     tigrc='"$EDITOR" "${XDG_CONFIG_HOME}/git/git_tigrc" -c "vsplit +set\ noma /etc/tigrc | 20 wincmd > | wincmd p"'
[[ -f "${XDG_CONFIG_HOME}/nnn/quitcd.bash_sh_zsh" ]] && . "${XDG_CONFIG_HOME}/nnn/quitcd.bash_sh_zsh"
#declare -x CMAKE_BUILD_PARALLEL_LEVEL="$(($(nproc)-2>0?$(nproc)-2:1))" in local aliases


# less command behaviour:
# +X : enable startup termcap
# -F : (not used) print to console if 1 page
# -q : medium-quiet
# -R : interpret escape-sequences
# -J : show status-column
# -N : show line numbers (off)
# -M : use long prompt
# -x3: use <N> as tabstop
# -#6: use <N> as the horizontal scroll amount
# -S : chop long lines
declare -x LESS='-+X -+F -qRJM -x3 -#6 -S'
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# https://github.com/mintty/mintty/issues/170#issuecomment-108889098
# disable mouse-scrolling in mintty for the alternate screen
# no longer needed: https://github.com/gwsw/less/issues/111
# echo $'\e[?7786l'

# thicker underscore cursor on mintty:
echo $'\e[?3c'

# grep colored output styling:
# https://askubuntu.com/a/1042242
# TODO declare -rx GREP_COLORS=''


# expand variables to their contained values,
# and don't suggest files for these commands:
#shopt -s direxpand
complete -d -o bashdefault -- cd ls lsa mkdir
complete -ab -A function -X '{_*,}' -- type
complete -A shopt shopt
complete -A stopped fg
complete -A running bg
complete -A helptopic help
complete -A variable unset

# suggest completions for an empty
# commandline with enabled builtins:
complete -A enabled -E


# startup the gpg and ssh agent:
# make the gpg-agent cache my password for one hour.
# https://help.github.com/en/github/authenticating-to-github/associating-an-email-with-your-gpg-key
#echo 'starting up gpg-agent daemon...'
export GPG_TTY=$(tty)
eval "(gpg-agent --daemon)" 2> /dev/null

[[ -z "${SSH_AUTH_SOCK}" ]] && eval "$(ssh-agent -s)"
#function ssh-agent() {
#    echo 'warning: an ssh agent has already been started.'
#    echo 'if you wish to use this executable, prefix with the command builtin.'
#    echo 'to kill all ssh-agents on windows, do:'
#    echo '  taskkill //F //FI "IMAGENAME eq ssh-agent.exe" //T'
#}
#readonly -f ssh-agent


source "$(dirname "${BASH_SOURCE[0]}")/prompt.sh"

#xkbcomp "$HOME/.config/xkb/xkb.xkb" $DISPLAY 2>/dev/null
# ^copy the above into /usr/share/X11/xkb/symbols/us
# Note: https://bugs.freedesktop.org/show_bug.cgi?id=78661
