#!/bin/bash
# Some ideas taken from https://github.com/mrzool/bash-sensible/blob/master/sensible.bash
set -eo pipefail

[[ "$MINGW64_HOME"     ]] &&      MINGW64_HOME="$(cygpath "$MINGW64_HOME")"
[[ "$JAVA_HOME"        ]] &&         JAVA_HOME="$(cygpath "$JAVA_HOME")"
[[ "$GRADLE_HOME"      ]] &&       GRADLE_HOME="$(cygpath "$GRADLE_HOME")"
[[ "$MONGODB_HOME"     ]] &&      MONGODB_HOME="$(cygpath "$MONGODB_HOME")"

# exit if not running interactively:
[[ "$-" =~ "i" ]] || return


# disable sending and receiving XON/XOFF
# (only one is actually necessary to do)
stty stop '' -ixoff
stty stop '' -ixon

# set codepage (on windows) to UTF-8
# https://docs.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
# mintty no longer needs this, but the new windows terminal does.
# https://github.com/msys2/msys2-runtime/pull/15
chcp.com 65001 2> /dev/null

shopt -s globstar
shopt -s extglob
shopt -s checkwinsize
export FUNCNEST=100


shopt -s histappend
declare -a histignore=(
    'fg' 'fg\ *' 'hist' 'history' 'hash' 'bind' 'clear'
    'config' 'inputrc' 'bashrc' 'als' 'alsl' 'vimrc' 'gitconfig' 'tigrc'
    'cd\ \.\.*' 'ls' 'lsa' 'clsa' 'lsen\ *'
    'todo'
    './build*' #'./main' 'npm\ run\ start'
    'tig' 'git\ status' 'git\ st' 'git\ br' 'git\ diff' 'git\ df'
)
export HISTIGNORE=
for pattern in "${histignore[@]}"; do
    HISTIGNORE+="$pattern"':'
done
unset histignore
export HISTCONTROL=ignoredups:ignorespace:erasedups
export HISTSIZE=1024
export HISTFILESIZE=2048
PROMPT_COMMAND='history -a' # Record each line as it gets issued


export NODE_ENV='development'
PATH+=":$(cygpath "${APPDATA}")/npm"
[[ -f "${XDG_CONFIG_HOME}/npm/completion" ]] && source "${XDG_CONFIG_HOME}/npm/completion"

export EDITOR='vim'
export CSCOPE_EDITOR='view'


source "${XDG_CONFIG_HOME}/bash/_xdg_compat.sh"

[[ -f "${XDG_CONFIG_HOME}/bash/_aliases.sh"        ]] && source "${XDG_CONFIG_HOME}/bash/_aliases.sh"
[[ -f "${XDG_CONFIG_HOME}/bash/_aliases__local.sh" ]] && source "${XDG_CONFIG_HOME}/bash/_aliases__local.sh"
alias   inputrc='"$EDITOR" "${XDG_CONFIG_HOME}/readline/inputrc"'
alias    bashrc='"$EDITOR" "${XDG_CONFIG_HOME}/bash/main.sh"'
alias       als='"$EDITOR" "${XDG_CONFIG_HOME}/bash/_aliases.sh"'
alias      alsl='"$EDITOR" "${XDG_CONFIG_HOME}/bash/_aliases__local.sh"'
alias     vimrc='"$EDITOR" "${XDG_CONFIG_HOME}/vim/main.vim"'
alias gitconfig='"$EDITOR" "${XDG_CONFIG_HOME}/git/config"'
alias     tigrc='"$EDITOR" "${XDG_CONFIG_HOME}/git/git_tigrc" -c "vsplit +set\ noma /etc/tigrc | 20 wincmd > | wincmd p"'


# less command behaviour:
# +X : enable startup termcap
# -F : (not used) print to console if 1 page
# -q : medium-quiet
# -R : interpret escape-sequences
# -J : show status-column
# -N : show line numbers (off)
# -M : use long prompt
# -x4: use <4> as tabstop
# -#N: use <N> as the horizontal scroll amount
declare -x LESS='-+X -qRJM -x4 -#4'

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
shopt -s direxpand
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
echo 'starting up gpg-agent daemon...'
export GPG_TTY=$(tty)
eval "(gpg-agent --daemon)" 2> /dev/null

# [[ -z "${SSH_AUTH_SOCK}" ]] && eval "$(ssh-agent -s)"
# function ssh-agent() {
#     echo 'warning: an ssh agent has already been started.'
#     echo 'if you wish to use this executable, prefix with the command builtin.'
#     echo 'to kill all ssh-agents, do:'
#     echo '  taskkill //F //FI "IMAGENAME eq ssh-agent.exe" //T'
# }
# readonly -f ssh-agent


# finalize prompt:
source "$(dirname "${BASH_SOURCE[0]}")""/_prompt.sh"

set +eo pipefail
