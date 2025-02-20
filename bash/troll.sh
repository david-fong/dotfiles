declare -r PS1="I am a prompt: "

# https://en.wikipedia.org/wiki/ANSI_escape_code
# https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

# set delete key to space-bar:
# this can be undone by logging out and in again.
stty erase ' '

stty eof 0x7f  # close terminal with backspace-key

# disables the following builtins:
enable -n enable cd echo

echo -e '\e[?1003h' # report mouse movement

# https://github.com/mintty/mintty/wiki/CtrlSeqs#bidirectional-rendering
# (mintty only) flips the screen horizontally
echo -e '\e[3 S'

# kill -s KILL $$

# do not echo input to the interactive shell:
stty -echo

echo -e '\e#8'      # fill screen with 'E's
echo -e '\e[?5h'    # reverse video brighness
echo -e '\e[25l'    # make cursor invisible
