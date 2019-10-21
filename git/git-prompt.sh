
# https://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/bash-prompt-escape-sequences.html

PS1='\[\033]0;\u@\H : $PWD\007\]\n'       # set window title
PS1="$PS1"'\[\033[32m\]\u@\H'"'"'$SHLVL'  # green  : user
PS1="$PS1"' \[\033[1;34m\]\@\[\033[22m\]' # blue   : time
PS1="$PS1"' \[\033[33m\]\w'               # yellow : path
if test -z "$WINELOADERNOEXEC"
then
    GIT_EXEC_PATH="$(git --exec-path 2>/dev/null)"
    COMPLETION_PATH="${GIT_EXEC_PATH%/libexec/git-core}"
    COMPLETION_PATH="${COMPLETION_PATH%/lib/git-core}"
    COMPLETION_PATH="${COMPLETION_PATH}/share/git/completion"
    if test -f "$COMPLETION_PATH/git-prompt.sh"
    then
        . "$COMPLETION_PATH/git-completion.bash"
        . "$COMPLETION_PATH/git-prompt.sh"
        PS1="$PS1"'\[\033[36m\]`__git_ps1`' # change color to cyan
    fi
fi
PS1="$PS1"'\[\033[0m\]\n$ '

