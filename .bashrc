
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
HISTCONTROL=ignoredups:ignorespace
HISTSIZE=1000
HISTFILESIZE=1500

export LINES COLUMNS # <- for .gitconfig

[ -f ~/'.myscripts/ansicode' ] && source ~/'.myscripts/ansicode'
[ -f ~/'.bash_aliases' ] && source ~/'.bash_aliases'
[ -f ~/'.bash_aliases_local' ] && source ~/'.bash_aliases_local'
alias bashrc='vim ~/.bashrc'
alias vimrc='vim ~/.vimrc'
alias als='vim ~/.bash_aliases'
alias alsl='vim ~/.bash_aliases_local'

export EDITOR='vim'
export CSCOPE_EDITOR='vim'

# startup the ssh agent:
[ "$SSH_AUTH_SOCK" ] && eval "$(ssh-agent -s)"

# finalize prompt:
readonly PS1
declare -rix PROMPT_DIRTRIM=5
declare -rxi PSLINES=`echo -e "$PS1" | wc --lines`

# go to the user's home directory:
if [ "$PWD" = '/' ]
then
   home
else
   clsa
fi

stty echo

