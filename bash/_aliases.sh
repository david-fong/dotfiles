#!/bin/bash
#set -eo pipefail

alias l='less'
alias g='git'
alias s='git s'
alias d='git d'
alias nom='pnpm'
alias nomx='pnpx'
alias mc='mc -u' # midnight-commander disable subshell due to startup time issues

alias n='nnn-quitcd -QAenH'
# Q don't prompt on quit
# A disable directory auto-enter on filter match
# e use $VISUAL or fallback to $EDITOR
## o open files on enter only
# n start in type-to-nav mode. toggle with ^N
# H show hidden files

alias greeting='clear; \echo -e "\n$(heading "$(date)")""\n"'
alias cyclelogin='\exec "$0" "$@" --init-file ~/.bash_profile'

alias rm='\rm -I --verbose'
alias hd='xxd -e -g1 -c32 -R always'
#alias jobs='jobs -l; tasklist | command grep agent'
alias hist='history | less +G'
#function hash() {
#    command hash "$@" | sort -r
#}

if [[ "$OCTAVE_HOME" ]]
    then alias octave='"$OCTAVE_HOME"/mingw64/bin/octave-cli --interactive'; fi


declare -a grepargs=('--line-number' '--color=auto')
grepargs+=('--exclude-dir={.git,bin,build,dist,compile,db,incremental_db,node_modules,.yarn,.vs,obj,packages,logs}')
if [[ -f "${XDG_CONFIG_HOME}/grep/excludefrom" ]]
    then grepargs+=('--exclude-from="${XDG_CONFIG_HOME}/grep/excludefrom"'); fi
alias fgr='\grep '"${grepargs[@]}"''
alias  gr='\grep '"${grepargs[@]}"' --extended-regexp'
unset grepargs

function rgr {
    grep -r --color=always "$@" | awk -F '[:]' -v OFS=':' 'f!=$1 {f=$1; print "\n"f} f==$1 {$1=""; printf "%34s",$2; $2=""; print}';
}


alias diff='\diff --side-by-side --suppress-common-lines --width="$COLUMNS" --color=auto'
#function manifest() {
#    local -ra choices="$(find -type f -name "*.jar")"
#    [[ "${#choices}" -le 0 ]] && return 1
#    select jarchoice in ${choices[@]}; do
#        [[ "$jarchoice" ]] && unzip -qc "$jarchoice" META-INF/MANIFEST.MF
#    done
#}


# spelling is hard
alias lag='lazygit'
alias gti='git'
alias it='git'
alias vm='mv'


function todo() {
    local -r todopath="${HOME}/.todo.md"
    #"$EDITOR" "$todopath" -c 'vnew +set\ noma | wincmd p'
    "$EDITOR" "$todopath"
}


alias ls='\ls -CX --color=auto --group-directories-first --width=90'
function lsa() {
    ls "$@" -o --almost-all --human-readable
}
alias clsa='clear'
function lsen() {
    for extension in "$@"; do
        echo
        lsa | \grep -Ei "\\S*[.]${extension}$" --
    done
}


# BOOKMARKED DIRECTORIES & DIRECTORY NAVIGATION:
alias root='\cd / && clsa'
function home() {
    clear
    stty -echo
    \echo -e "\n$(heading "$(date)")""\n"
    \cd "${HOME}" && ls --width=75 --hide=[nN][tT][uU][sS]*
    stty echo
}
alias config='\cd ${XDG_CONFIG_HOME} && clsa'



function bind() {
    if [[ -z "$*" ]]; then
        local -r filterout="(self-insert)|(do-lowercase-version)"
        bind -p | command grep -vT --color=always "$filterout" | less
    else
        command bind "$@"
    fi
}


# $1: string for heading text
function heading() {
    local payload="$1"
    [ "$payload" ] && payload=' '"$payload"' '
    local line=''
    local -ri payloadlen="${#payload}"
    printf -v line '%*s' "$((COLUMNS-payloadlen-3))"
    line="${line// /=}"
    echo -ne '==='"$payload"
    printf '%s\n' "$line"
}


# make functions unmodifiable:
#readonly -f todo lsa lsen home heading
#export   -f todo lsa lsen home heading

#set +eo pipefail
