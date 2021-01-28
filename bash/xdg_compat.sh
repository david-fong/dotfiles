#!/bin/bash
# https://wiki.archlinux.org/index.php/XDG_Base_Directory
# https://web.archive.org/web/20180827160401/plus.google.com/+RobPikeTheHuman/posts/R58WgWwN9jp


mkdir -p "$XDG_DATA_HOME"/bash
mkdir -p "$XDG_DATA_HOME"/tig

declare -rx          HISTFILE="${XDG_DATA_HOME}/bash/history"
declare -rx NODE_REPL_HISTORY="${XDG_DATA_HOME}/.node_repl_history"
declare -rx      LESSHISTFILE="${XDG_DATA_HOME}/.less_history"

declare -rx       INPUTRC="${XDG_CONFIG_HOME}/readline/inputrc"
declare -rx       VIMINIT='source ${XDG_CONFIG_HOME}/vim/vimrc'
declare -rx    TIGRC_USER="${XDG_CONFIG_HOME}/git/tigrc_colorstrings"
declare -rx PYTHONSTARTUP="${XDG_CONFIG_HOME}/python/startup.py"
             PYTHONHOME+=":${XDG_CONFIG_HOME}/python/"
declare -rx       LESSKEY="${XDG_CONFIG_HOME}/less/lesskey"

lesskey "${XDG_CONFIG_HOME}/less/lesskey"

