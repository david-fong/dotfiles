
# note to self: in a script, BASH_SOURCE is an array with
# entry 0 = full file path to script
# entry 1 = full file path to pwd of script caller

# ------------------------------------------------------
# REGULAR USE:
# ------------------------------------------------------
alias greeting='\echo -e "\033c\n""$(heading "$(date)")""\n"'
alias cyclelogin='\exec "$0" "$@"; clsa'

alias rm='\rm -I --verbose'
alias hd='xxd -e -g4 -c32'
alias jobs='jobs -l'
alias hist='history | tail -17'


declare -a grepargs=('--line-number' '--text' '--color=auto')
for exdir in '.git' 'build' 'compile' 'db'; do
    grepargs+=('--exclude-dir="'"$exdir"'"')
done
[[ ! -f ~/.grepexcludefrom ]] && touch ~/.grepexcludefrom
grepargs+=('--exclude-from="${HOME}/.grepexcludefrom"' '--extended-regexp')
alias grep='\grep '"${grepargs[@]}"''
unset grepargs


alias search='grep --recursive --byte-offset --include="*.java"'
alias diff='\diff --side-by-side --suppress-common-lines --width="$COLUMNS" --color=auto'
function manifest() {
   local -ra choices="$(find -type f -name "*.jar")"
   [[ "${#choices}" -le 0 ]] && return 1
   select jarchoice in ${choices[@]}; do
      [[ "$jarchoice" ]] && unzip -qc "$jarchoice" META-INF/MANIFEST.MF
   done
}



alias gti='git'
alias cim='vim' # typing is hard.
alias vimr='vim -R'
alias vims='vim -S'
alias swp='find "$@" -type f -name "*.swp"'



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
      "$EDITOR" "$todopath"
   fi
}
alias todoe='todo -e'



alias ls='\ls -CX --color=auto --group-directories-first'
function __lsa() {
    ls "$@" -o --almost-all --human-readable
}
function lsa() {
   tput rmam
   local -r OLD_GREP_COLORS="$GREP_COLORS"
   export GREP_COLORS='ms=38;5;246' # dull blue
   local -x coloropt='--color=never'
   if [[ -t 1 ]]; then
      coloropt='--color=always'
   fi
   local -r listing="$(__lsa "$@" "$coloropt")"
         \grep -E "^[^-]" <<< "$listing"
`#echo`; \grep -E "^[-]"  <<< "$listing" \
       | \grep -E --color=never "\\s[.]?[^. ]+$"
`#echo`; \grep -E "^[-].*\\S+[.][^. ]+$"  <<< "$listing" \
       | \grep -E "$coloropt" "[.][^. ]+$"
   export GREP_COLORS="$OLD_GREP_COLORS"
   tput smam
   return 0
}
alias clsa='greeting; lsa'
function lsen() {
   for extension in "$@"; do
      echo
      __lsa | \grep -Ei "\\S*[.]${extension}$" --
   done
}



# BOOKMARKED DIRECTORIES & DIRECTORY NAVIGATION:
alias root='\cd / && clsa'
alias cdrive='\cd /c && clsa'
function home() {
   stty -echo
   greeting
   \cd ~ && time ls --width=70 --hide=[nN][tT][uU][sS]*
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
readonly -f manifest todo __lsa lsa lsen home numdirents yes heading
export   -f manifest todo __lsa lsa lsen home numdirents yes heading

