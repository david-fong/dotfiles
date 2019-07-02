
# REGULAR USE:
alias rm='\rm -I'

alias ls='\ls -CX --color=auto --group-directories-first'
alias lss='ls --width=70'
lsa() {
    tput rmam;
    ls "$@" -o --almost-all --human-readable;
    tput smam;
    return 0;
}

alias clss='clear; lss'
alias clsa='clear; lsa'

alias lst='lsa -tr'
alias lsg='lsa | grep -i'

alias root='\cd / && clsa'
alias home='\cd ~ && clear; lss --hide=[nN][tT][uU][sS]*' 
alias school='\cd ~/Documents/UBC/YEAR3/SEM1/ && clsa'
alias e='\cd .. && lss'
cdd() { cd "$@" && ls; }


# JUST FOR KICKS:
alias ohno='/cat /dev/random'
alias pasta='/cat /dev/clipboard'
alias soundcheck='/echo -e "\a"'

