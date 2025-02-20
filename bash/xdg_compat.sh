#!/bin/sh
# https://wiki.archlinux.org/index.php/XDG_Base_Directory
# https://web.archive.org/web/20180827160401/plus.google.com/+RobPikeTheHuman/posts/R58WgWwN9jp

mkdir -p "${XDG_DATA_HOME}/bash"
mkdir -p "${XDG_STATE_HOME}/bash"
mkdir -p "${XDG_DATA_HOME}/tig"
mkdir -p "${XDG_DATA_HOME}/less"
mkdir -p "${XDG_DATA_HOME}/gradle"
mkdir -p "${XDG_CACHE_HOME}/ccache"
mkdir -p "${XDG_CACHE_HOME}/ipython"
alias yarn='yarn --use-yarnrc "$XDG_CONFIG_HOME/yarn/config"'
#[[ ! -f "${XDG_DATA_HOME}/bash-completion/completions/cmake" ]] && ln -s /snap/cmake/current/share/bash-completion/completions/* "${XDG_DATA_HOME}/bash-completion/completions"

export CPM_SOURCE_CACHE="${XDG_CACHE_HOME}/CPM"
export PYTHONPYCACHEPREFIX="${XDG_CACHE_HOME}/python"

export          HISTFILE="${XDG_STATE_HOME}/bash/history"
export NODE_REPL_HISTORY="${XDG_STATE_HOME}/.node_repl_history"
export       GDBHISTFILE="${XDG_STATE_HOME}/gdb/history"
export    PYTHON_HISTORY="${XDG_STATE_HOME}/python/history"
export    SQLITE_HISTORY="${XDG_STATE_HOME}/sqlite_history"
alias wget='\wget --hsts-file="${XDG_CACHE_HOME}/wget-hsts"'

export       INPUTRC="${XDG_CONFIG_HOME}/readline/inputrc"
export RIPGREP_CONFIG_PATH="${XDG_CONFIG_HOME}/grep/ripgrep"
export       VIMINIT='. $XDG_CONFIG_HOME/vim/main.vim' # annoyingly, the ${} form gets interpreted (and choked-upon) by CMake Tools for reasons beyond my comprehension and patience.
export    TIGRC_USER="${XDG_CONFIG_HOME}/git/tigrc_colorstrings"
export DOCKER_CONFIG="${XDG_CONFIG_HOME}/docker"
#export        WGETRC="${XDG_CONFIG_HOME}/wgetrc" # currently not used
#export PYTHONSTARTUP="${XDG_CONFIG_HOME}/python/startup.py"
# PYTHONHOME+=":${XDG_CONFIG_HOME}/python/"
export NPM_CONFIG_USERCONFIG="${XDG_CONFIG_HOME}/npm/npmrc"
export CONAN_USER_HOME="${XDG_CONFIG_HOME}"

export GRADLE_USER_HOME="${XDG_DATA_HOME}/gradle"
export       CARGO_HOME="${XDG_DATA_HOME}/cargo"
export      RUSTUP_HOME="${XDG_DATA_HOME}/rustup"
