
# note to self: in a script, BASH_SOURCE is an array with
# entry 0 = full file path to script
# entry 1 = full file path to pwd of script caller

# ------------------------------------------------------
# REGULAR USE:
# ------------------------------------------------------
alias rm='\rm -I'
alias cyclelogin='exec "$0" "$@" && clear'

alias ls='\ls -CX --color=auto --group-directories-first'
alias lss='ls --width=70'
lsa() {
   tput rmam
   lss "$@" -o --almost-all --human-readable
   tput smam
   return 0
}
alias clss='clear; lss'
alias clsa='clear; lsa'

alias lst='lsa -tr'
alias lsg='lsa | grep -i'

alias root='\cd / && clsa'
alias home='\cd ~; echo -e "\033c\n`date`\n"; lss --hide=[nN][tT][uU][sS]*' 
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
   echo -n "$num"
}
yes() {
   local -ar colors=(red yellow green cyan blue magenta)
   local -i i=0
   local payload="$1"
   readonly payload="${payload:=y\n}"
   while : #sleep '0.01'
   do
      ansicode sgr enclose "$payload" "${colors[$i]}"
      let i="($i+1)"%"${#colors[@]}"
   done
}


# disable writes to functions:
readonly -f lsa cdd numdirents yes

