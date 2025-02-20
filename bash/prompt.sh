#!/bin/bash
# https://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/bash-prompt-escape-sequences.html

if [ -z "$WINELOADERNOEXEC" ]
then
	GIT_EXEC_PATH="$(git --exec-path 2>/dev/null)"
	COMPLETION_PATH="${GIT_EXEC_PATH%/libexec/git-core}"
	COMPLETION_PATH="${COMPLETION_PATH%/lib/git-core}"
	COMPLETION_PATH="${COMPLETION_PATH}/share/git/completion"
	if [ -f "$COMPLETION_PATH/git-prompt.sh" ]
	then
		. "$COMPLETION_PATH/git-completion.bash"
		#. "$COMPLETION_PATH/git-prompt.sh"
	fi
fi

# function fast_git_ps1 ()
# {
# 	printf -- "$(\git branch --show-current 2>/dev/null)"
# }
# PS1="\[\033]0;\u@\H : $PWD\007\]\n\[\033[32m\]\u@\H \[\033[1;34m\]\@\[\033[22m\] \[\033[33m\]\w\[\033[36m\] ("'`fast_git_ps1`'")\[\033[0m\]\n$ "
# PS1="\[\033]0;\u@\H : $PWD\007\]\n\[\033[32m\]\u@\H \[\033[1;34m\]\@\[\033[22m\] \[\033[33m\]\w\[\033[36m\] "'`__ps1_face`'"\[\033[37m\]\n$\[\033[0m\] "
# PROMPT_COMMAND='__git_ps1 "\[\033]0;\u@\H : $PWD\007\]\n\[\033[32m\]\u@\H \[\033[1;34m\]\@\[\033[22m\] \[\033[33m\]\w\[\033[36m\]" "\[\033[0m\]\n$ "'

# function __ps1_face(){
# 	declare -a FACES=('(._.)' '(._.)' '(._.)' '(._.)' '(._.)' '(._.)' '(._.)' '_(._. _)_' '_(_ ._.)_' '(.-.)' '_( ._.) . (._. )_')
# 	echo "${FACES[$RANDOM % ${#FACES[@]}]}"
# }
# readonly -f __ps1_face
PS1='\n\[\033[32m\]\u@\H \[\033[33m\]\w\[\033[36m\] (._.)\[\033[37m\]\n$\[\033[0m\] '

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
	debian_chroot=$(cat /etc/debian_chroot)
fi
# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
	PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
	;;
*)
	;;
esac

export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

declare -i PROMPT_DIRTRIM=5
