
# exit if not running interactively:
[[ "$-" =~ "i" ]] || return

# Not related, but written here in case I forget what I did:
# Computer\HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer\NoUninstallFromStart

stty -echo
clear
declare -rxi PSLINES=`echo -e "$PS1" | wc --lines`

shopt -s globstar

shopt -s histappend
HISTCONTROL=ignoredups:ignorespace
HISTSIZE=1000
HISTFILESIZE=1500

declare -rx PERSONAL_PROJECT_HOME=~/"IdeaProjects/ucst"
export LINES COLUMNS # <- the only way .gitconfig can see environment variables

[ -f ~/'.myscripts/ansicode' ] && source ~/'.myscripts/ansicode'
[ -f ~/'.myscripts/heading' ] && source ~/'.myscripts/heading'
[ -f ~/'.bash_aliases' ] && source ~/'.bash_aliases'
[ -f ~/'.bash_aliases_local' ] && source ~/'.bash_aliases_local'
alias bashrc='vim ~/.bashrc'
alias vimrc='vim ~/.vimrc'
alias als='vim ~/.bash_aliases'
alias alsl='vim ~/.bash_aliases_local'

# also see /etc/profile.d/git-prompt.sh
# random note: can open control panel with windows + pause/break

# startup the ssh agent:
[ "$SSH_AUTH_SOCK" ] && eval "$(ssh-agent -s)"

# go to the user's home directory:
[ "$PWD" = '/' ] && home
readonly PS1
stty echo

