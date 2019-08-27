
# note to self: in a script, BASH_SOURCE is an array with
# entry 0 = full file path to script
# entry 1 = full file path to pwd of script caller

# ------------------------------------------------------
# REGULAR USE:
# ------------------------------------------------------
alias rm='\rm -I --verbose'

alias diff='\diff --side-by-side --suppress-common-lines --width="$COLUMNS" --color=auto'
alias hd='xxd -e -g4 -c32'
alias grep='\grep --line-number --text --extended-regexp --color=auto'
alias search='grep --recursive --byte-offset --include="*.java"'

alias cyclelogin='\exec "$0" "$@"; flsa'
alias greeting='\echo -e "\033c\n`date`\n"'
todo() {
   local -r todopath=~/".todo"
   if [[ "$1" = '-e' ]]
   then
      cat "$todopath"
      return
   else
      vim "$todopath"
   fi
}
alias todoe='todo -e'

alias ls='\ls -CX --color=auto --group-directories-first'
alias lss='ls --width=70'
lsa() {
   tput rmam
   ls "$@" -o --almost-all --human-readable
   tput smam
   return 0
}
alias clsa='greeting; lsa'

alias root='\cd / && (clsa)'
alias cdrive='\cd /c && (clsa)'
alias sandbox='\cd ~/"Documents/test/GitSandbox" && (clsa)'
alias project='\cd "$MY_CURRENT_PERSONAL_PROJECT_HOME" && (clsa)'
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
alias school='\cd ~/Documents/UBC/YEAR3/SEM1/ && (clsa)'
alias e='\cd .. && (clsa)'
alias ee='\cd ../.. && (clsa)'
alias eee='\cd ../../.. && (clsa)'
alias eeee='\cd ../../../.. && (clsa)'
alias eeeee='\cd ../../../../.. && (clsa)'
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
readonly -f todo lsa home cdd numdirents yes

