
# exit if not running interactively:
[ -z PS1 ] && return

# Not related, but here in case I forget what I did:
# Computer\HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer\NoUninstallFromStart

stty -echo
readonly PS1
clear

shopt -s histappend
HISTCONTROL=ignoredups:ignorespace
HISTSIZE=1000
HISTFILESIZE=1500

[ -f ~/.myscripts/ansicode ] && . ~/.myscripts/ansicode
[ -f ~/.myscripts/heading ] && . ~/.myscripts/heading
[ -f ~/.bash_aliases ] && . ~/.bash_aliases
# also see /etc/profile.d/git-prompt.sh

# go to the user's home directory:
[ $PWD = '/' ] && home
stty echo

