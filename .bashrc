
# exit if not running interactively:
[ -z PS1 ] && return


# do not duplicate lines in the history file:
HISTCONTROL=ignoredups:ignorespace
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=1500


# run the alias-setup script:
[ -f ~/.bash_aliases ] && . ~/.bash_aliases


# go to the user's home directory:
#[ $PWD = / ] && home
school
cd .timetable && . ./.xterm_format_constants
lsa
termsection "roses are red\n" red
termsection "violets are blue\n" blue
termsection "the next line will blink\n" green
termsection "potato\n" blink

