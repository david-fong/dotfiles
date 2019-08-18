
# note to self: in a script, BASH_SOURCE is an array with
# entry 0 = full file path to script
# entry 1 = full file path to pwd of script caller

# ------------------------------------------------------
# REGULAR USE:
# ------------------------------------------------------
alias rm='\rm -I'
alias diff='\diff --side-by-side --suppress-common-lines --width="$COLUMNS" --color=auto'
alias hd='xxd -e -g4 -c32'
alias grep='\grep --line-number --color=auto'
alias search='grep --recursive --ignore-case --byte-offset --include="*.java" --extended-regexp'
alias cyclelogin='\exec "$0" "$@"; greeting; lsa'
alias greeting='\echo -e "\033c\n`date`\n"'

alias ls='\ls -CX --color=auto --group-directories-first'
alias lss='ls --width=70'
lsa() {
   tput rmam
   ls "$@" -o --almost-all --human-readable
   tput smam
   return 0
}
alias clss='clear; lss'
alias clsa='greeting; lsa'

alias lst='lsa -tr'

alias root='\cd / && (greeting; lsa)'
alias cdrive='\cd /c && (greeting; lsa)'
home() {
   stty -echo
   greeting
   gitwd() { git rev-parse --show-toplevel 2>/dev/null; }
   if [[ -n `gitwd` && `\pwd -W` != `gitwd` ]]; then
      \cd `gitwd`
      lsa
   else
      \cd ~
      lss --hide=[nN][tT][uU][sS]*
   fi
   unset gitwd
   stty echo
}
alias school='\cd ~/Documents/UBC/YEAR3/SEM1/ && clsa'
alias e='\cd .. && lss'
cdd() {
   cd "$@" && ls
}


# ------------------------------------------------------
# JUST FOR KICKS:
# ------------------------------------------------------
alias ohno='\cat /dev/random'
alias pasta='\cat /dev/clipboard'
alias soundcheck='\echo -ne "\a"'
numdirents() {
   local -a dirents=(*)
   local -i num="${#dirents}"
   dirents=(.*)
   num+="${#dirents}"
   echo -n "$((num-2))"
}
yes() {
   local -a colors=(red yellow green cyan blue magenta)
   local -i i=0
   while [[ i -lt "${#colors[@]}" ]]; do
      colors["$i"]=`ansicode sgr start "${colors[$i]}"`
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


# disable writes to functions:
readonly -f lsa home cdd numdirents yes

