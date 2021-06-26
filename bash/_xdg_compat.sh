#!/bin/bash
# https://wiki.archlinux.org/index.php/XDG_Base_Directory
# https://web.archive.org/web/20180827160401/plus.google.com/+RobPikeTheHuman/posts/R58WgWwN9jp
set -eo pipefail

mkdir -p "${XDG_DATA_HOME}/bash"
mkdir -p "${XDG_DATA_HOME}/tig"
mkdir -p "${XDG_DATA_HOME}/less"
alias yarn='yarn --use-yarnrc "$XDG_CONFIG_HOME/yarn/config"'

declare -rx          HISTFILE="${XDG_DATA_HOME}/bash/history"
declare -rx NODE_REPL_HISTORY="${XDG_DATA_HOME}/.node_repl_history"
declare -rx      LESSHISTFILE="${XDG_DATA_HOME}/.less_history"

declare -rx       INPUTRC="${XDG_CONFIG_HOME}/readline/inputrc"
declare -rx       LESSKEY="${XDG_DATA_HOME}/less/lesskey"
declare -rx RIPGREP_CONFIG_PATH="${XDG_CONFIG_HOME}/grep/ripgrep"
declare -rx       VIMINIT='source ${XDG_CONFIG_HOME}/vim/main.vim'
declare -rx    TIGRC_USER="${XDG_CONFIG_HOME}/git/tigrc_colorstrings"
declare -rx DOCKER_CONFIG="$XDG_CONFIG_HOME"/docker

declare -rx PYTHONSTARTUP="${XDG_CONFIG_HOME}/python/startup.py"
             PYTHONHOME+=":${XDG_CONFIG_HOME}/python/"
declare -rx NPM_CONFIG_USERCONFIG="${XDG_CONFIG_HOME}/npm/npmrc"
declare -rx   CARGO_HOME="${XDG_DATA_HOME}/cargo"
[[ -f "${XDG_DATA_HOME}/emsdk/emsdk_env.sh" ]] && source "${XDG_DATA_HOME}/emsdk/emsdk_env.sh"

# note: this must go after the declaration of LESSKEY.
lesskey --output="${XDG_DATA_HOME}/less/lesskey" -- "${XDG_CONFIG_HOME}/less/lesskey"

set +eo pipefail
