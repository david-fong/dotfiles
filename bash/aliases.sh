#!/bin/bash
alias l='less'
alias g='git'
alias s='git s'
alias d='git d'
alias nom='pnpm'
alias nomx='pnpx'
alias utc='date --rfc-3339=seconds -u'
#alias mc='mc -u' # midnight-commander disable subshell due to startup time issues

alias ls='\ls -CX --color=auto --group-directories-first --width=90'
function lsa() {
	ls "$@" -o --almost-all --human-readable
}
alias config='\cd ${XDG_CONFIG_HOME} && clear'

[ -x "$(command -v nnn)" ] && alias n='nnn-quitcd'

alias rm='\rm -I --verbose'
alias hd='xxd -e -g1 -c32 -R always'
#alias jobs='jobs -l; tasklist | command grep agent'
alias hist='history | less +G'
#function hash() {
#    command hash "$@" | sort -r
#}

function todo() {
	local -r todopath="${HOME}/.todo.md"
	#"$EDITOR" "$todopath" -c 'vnew +set\ noma | wincmd p'
	"$EDITOR" "$todopath"
}

# if [[ "$OCTAVE_HOME" ]]; then alias octave='"$OCTAVE_HOME"/mingw64/bin/octave-cli --interactive'; fi

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

[ -x "$(command -v cmake)" ] && alias cmake-play-build='cmake -Wdev -S . -B build --fresh -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -G "Ninja Multi-Config" -DCMAKE_CXX_COMPILER=g++'

# spelling is hard
#alias lag='lazygit'
#alias gti='git'
#alias it='git'
#alias vm='mv'

function bind() {
	if [[ -z "$*" ]]; then
		local -r filterout="(self-insert)|(do-lowercase-version)"
		bind -p | command grep -vT --color=always "$filterout" | less
	else
		command bind "$@"
	fi
}

function secret() {
	cd ~
	gocryptfs ~/.secret ~/secret
	cd secret
	vim -i .viminfo .
	unmount ~/secret
	# TODO this doesn't handle when user puts vim in background with ctrl+z
}

alias cyclelogin='\exec "$0" "$@" --init-file ~/.bash_profile'

# make functions unmodifiable:
#readonly -f todo lsa
#export   -f todo lsa
