
# exit if not running interactively:
[[ "$-" =~ "i" ]] || return



# Not related, but written here in case I forget what I did:
# Computer\HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer\NoUninstallFromStart
# right-click recycle bin and check the "prompt before moving to recycle-bin" box
# random note: can open control panel with windows + pause/break
# don't turn on "lower screen brightness in battery saving mode". seems to lock screen brightness until next computer restart.

stty -echo

shopt -s globstar

shopt -s histappend
export HISTCONTROL=ignoredups:ignorespace
export HISTIGNORE='fg*:hist*:ls:ls\ *:lsa:lsa\ *:clsa:lesn\ *:vims:vims\ *:todo*:clear'
export HISTSIZE=1000
export HISTFILESIZE=1500

export LINES COLUMNS # for .gitconfig

[[ -f ~/'.myscripts/ansicode' ]] && source ~/'.myscripts/ansicode'
[[ -f ~/'.bash_aliases'       ]] && source ~/'.bash_aliases'
[[ -f ~/'.bash_aliases_local' ]] && source ~/'.bash_aliases_local'
alias bashrc='"$EDITOR" ~/.bashrc'
alias  vimrc='"$EDITOR" ~/.vimrc'
alias    als='"$EDITOR" ~/.bash_aliases'
alias   alsl='"$EDITOR" ~/.bash_aliases_local'

export EDITOR='vim'
export CSCOPE_EDITOR='view'

# startup the ssh agent:
[ "$SSH_AUTH_SOCK" ] && eval "$(ssh-agent -s)"

# finalize prompt:
readonly PS1
declare -rxi PROMPT_DIRTRIM=5
declare -rxi PSLINES="$(echo -e "$PS1" | wc --lines)"

# grep colored output styling:
# https://www.gnu.org/software/grep/manual/grep.html#index-GREP_005fCOLORS-environment-variable
# TODO declare -rx GREP_COLORS=''



# go to the user's home directory:
if [[ "$PWD" = '/' || "$PWD" = "$HOME" ]]
then home; else clsa; fi

stty echo

