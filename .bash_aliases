
# note to self: in a script, BASH_SOURCE is an array with
# entry 0 = full file path to script
# entry 1 = full file path to pwd of script caller

# ------------------------------------------------------
# REGULAR USE:
# ------------------------------------------------------
alias greeting='\echo -e "\033c\n$(date)\n"'
alias cyclelogin='\exec "$0" "$@"; clsa'

alias rm='\rm -I --verbose'
alias hd='xxd -e -g4 -c32'
alias jobs='jobs -l'
alias grep='\grep --line-number --text --extended-regexp --color=auto'
alias search='grep --recursive --byte-offset --include="*.java"'
alias diff='\diff --side-by-side --suppress-common-lines --width="$COLUMNS" --color=auto'
function manifest() {
   local -ra choices="$(find -type f -name "*.jar")"
   [[ "${#choices}" -le 0 ]] && return 1
   select jarchoice in ${choices[@]}; do
      [[ "$jarchoice" ]] && unzip -qc "$jarchoice" META-INF/MANIFEST.MF
   done
}

alias cim='vim' # typing is hard.
alias vimr='vim -R'
function vim() {
   local -r STTYOPTS="$(stty --save)"
   stty stop '' -ixoff # temp disable ctrl+s
   stty stop '' -ixon  # temp disable ctrl+q
   command vim "$@" #'+star' start vim in insert mode:
   stty "$STTYOPTS"
}
function todo() {
   local -r todopath=~/".todo.md"
   if [[ "$1" = '-e' ]]
   then
      echo; heading "TODO"
      tput rmam
      cat "$todopath"
      heading
      tput smam
   else
      vim "$todopath"
   fi
}
alias todoe='todo -e'

# LISTING DIRECTORY CONTENTS:
alias ls='\ls -CX --color=auto --group-directories-first'
function lsa() {
   tput rmam
   ls "$@" -o --almost-all --human-readable
   tput smam
   return 0
}
alias clsa='greeting; lsa'


# BOOKMARKED DIRECTORIES & DIRECTORY NAVIGATION:
alias root='\cd / && clsa'
alias cdrive='\cd /c && clsa'
function home() {
   stty -echo
   greeting
   \cd ~
   ls --width=70 --hide=[nN][tT][uU][sS]*
   unset gitwd
   stty echo
}
alias githome='\cd "$(git rev-parse --show-toplevel 2>/dev/null)" && clsa'
alias e='\cd .. && clsa'
alias ee='\cd ../.. && clsa'
alias eee='\cd ../../.. && clsa'
alias eeee='\cd ../../../.. && clsa'
alias eeeee='\cd ../../../../.. && clsa'



# ------------------------------------------------------
# JUST FOR KICKS:
# ------------------------------------------------------
alias paste='\cat /dev/clipboard'
alias soundcheck='\echo -ne "\a"'
function numdirents() {
   local -a dirents=(*)
   local -i num="${#dirents}"
   dirents=(.*)
   num+="${#dirents}"
   echo -n "$((num-2))"
}
function yes() {
   local -a colors=(red yellow green cyan blue magenta)
   local -i i=0
   while [[ i -lt "${#colors[@]}" ]]; do
      colors["$i"]="$(ansicode sgr start "${colors[$i]}")"
      i+=1
   done; i=0; readonly colors
   local payload="$@"
   readonly payload="${payload:=y\n}"
   trap 'echo -ne "\033[0m"; trap - SIGINT; return 0' SIGINT
   while : #sleep '0.01'
   do
      echo -ne "${colors[$i]}""$payload"
      let i="($i+1)"%"${#colors[@]}"
   done
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
readonly -f manifest vim todo lsa home numdirents yes heading
export   -f manifest vim todo lsa home numdirents yes heading

