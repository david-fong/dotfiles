
# exit if not running interactively:
[[ "$-" =~ "i" ]] || return



# Not related, but written here in case I forget what I did:
# Computer\HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer\NoUninstallFromStart
# right-click recycle bin and check the "prompt before moving to recycle-bin" box
# random note: can open control panel with windows + pause/break
# don't turn on "lower screen brightness in battery saving mode". seems to lock screen brightness until next computer restart.

# stty -echo

stty stop '' -ixoff # disable ctrl+s ( pause console output)
stty stop '' -ixon  # disable ctrl+q (resume console output)
shopt -s globstar
export FUNCNEST=100

shopt -s histappend
declare -a histignore=(
    'fg*' 'hist' 'history' 'clear'
    'bashrc' 'als' 'alsl' 'gitconfig' 'vimrc'
    'ls' 'lsa' 'lsa\ *' 'clsa' 'lsen\ *'
    'vims' 'vims\ *' 'todo*'
    'git\ status' 'git gra' 'git\ graph' 'git\ grpah' 'git\ diff*'
)
export HISTIGNORE=
for pattern in "${histignore[@]}"; do
    HISTIGNORE+="$pattern"':'
done
unset histignore
export HISTCONTROL=ignoredups:ignorespace
export HISTSIZE=1000
export HISTFILESIZE=1500

export LINES COLUMNS # for .gitconfig

# https://www.gnu.org/software/bash/manual/html_node/A-Programmable-Completion-Example.html#A-Programmable-Completion-Example
[[ -f ~/.myscripts/comp_cd.sh ]] && source ~/.myscripts/comp_cd.sh
[[ -f ~/.myscripts/ansicode   ]] && source ~/.myscripts/ansicode
[[ -f ~/.bash_aliases         ]] && source ~/.bash_aliases
[[ -f ~/.bash_aliases_local   ]] && source ~/.bash_aliases_local
alias    bashrc='"$EDITOR" ~/.bashrc'
alias     vimrc='"$EDITOR" ~/.vimrc'
alias       als='"$EDITOR" ~/.bash_aliases'
alias      alsl='"$EDITOR" ~/.bash_aliases_local'
alias gitconfig='"$EDITOR" ~/.gitconfig'

export EDITOR='vim'
export CSCOPE_EDITOR='view'

# startup the ssh agent:
[ "$SSH_AUTH_SOCK" ] && eval "$(ssh-agent -s)"

# less command behaviour:
declare -rx LESS='-+X --ignore-case --quiet --raw-control-chars'

# finalize prompt:
readonly PS1
declare -rxi PROMPT_DIRTRIM=5
declare -rxi PSLINES="$(echo -e "$PS1" | wc --lines)"

# grep colored output styling:
# https://askubuntu.com/a/1042242
# TODO declare -rx GREP_COLORS=''



# go to the user's home directory:
if [[ "$PWD" = '/' || "$PWD" = "$HOME" ]]
then home; else clsa; fi

# stty echo

