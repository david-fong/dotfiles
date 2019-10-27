
# :breifcase: Darcy

"darcy" is how I like to slur the pronunciation of ".\*rc", which is the [fileglob pattern](tldp.org/LDP/GNU-Linux-Tools-Summary/html/x11655.htm) for typical standalone [run-configuration](wikipedia.org/wiki/Configuration_file) files. Most of the contents of this repo no longer follow that glob pattern ever since I moved everything to fall under one directory, but I want to keep the name because I like how it sounds.

You will notice that I embed a lot of links in this readme- even ones that you may feel are redundant- and that I don't speak from a very technical point of view. this is mostly because I am not an expert at using tools in the terminal environment, but also because I write this in hopes to encourage some of my friends to warm up to working in a terminal by making changes that make it more liveable (from my point of view), and providing links to the places that helped me learn about its different components.

### :gift: How to use it
As I said, everything is under one directory, which means less clutter, and easier portability. All you need to do to use my environment is to clone and copy this repo to the directory specified by the environment variable ["XGD\_CONFIG\_HOME"](standards.freedesktop.org/basedir-spec/basedir-spec-latest.html), which by convention is usually ~/.config/, if set by default. You should source :/[git/bashrc](git/bashrc) in your ~/.bash\_profile file, or whatever is passed as the --init-file argument when invoking bash. You can put a gitconfig-style file in /git/config\_\_local containing your name and email. Similarly, you can put machine-local bash run-config comands in /bash/aliases\_\_local.

### :turtle: Why I do this
I like to poke around and explore things. To me, reading about different parts of the terminal environment is like going on a treasure hunt. And while half the time I don't even know what I'm looking for, I enjoy almost every minute of it. At first, the question that always came up in my mind was "why is *<thing that doesn't follow conventions of modern applications>* this way?". And as I explored and learned about different pieces of the bigger picture, I started to see connections and how the pieces build on top of, or around each other.

For example, I wondered why vim doesn't save buffers using Ctrl+S by default. As I learned more about vim and started trying to write keymappings, I found out that Ctrl+S is reserved for manual [XON/XOFF flow-control](wikipedia.org/wiki/Software_flow_control) in most terminals, which exists because before terminals were emulated by modern computers, which can scroll through scrollback buffers quite quickly, people needed a mechanism to pause a terminal's output so the operator could actually read it. vim, for the most part, being a superset of VI, followed in VI's footsteps to honor the terminal's [default ownership](retrocomputing.stackexchange.com/questions/7263/history-of-ctrl-s-and-ctrl-q-for-flow-control) of that key-sequence. I found that this behaviour could be disabled using the stty (set teletype) command, which allowed me to map the update command in vim to Ctrl+S. As an aside, if there are any hardcore vim users shaking their fists right now saying I'm using vim wrong, I disagree. I think that if you leverage the configurability of a tool to make it work better for yourself, you are doing it exactly right.

If you're wondering why I don't use WSL, it's because when I started using git-for-windows, I had absolutely no idea what was going on, and it was hard for me to do or find worthwhile pretty much anything I saw. I've come a long way since then, and I may look at switching to WSL in the future, but not until I feel like I'm being limited by MinGW.



## :balloon: A Bird's Eye View

This is a high level view of what I have learned about terminal-related facilities. Because I learned it on my own, the things I have to say are in the words of a beginner. I may have accidentally gotten something wrong, so if you notice a mistake or something that can be improved, please shoot me a message and correct me!

program                 | description
:----------------------:| -------------------------
:shell:<br>bash         | a shell based on sh with features from other shells like csh and ksh. shells allow you to interact with your operating system's kernel by providing certain services, and making those callable through a command-line interface. those services include creating and destroying files and directories, writing to and reading from files, performing file processing, and navigating directories, job / process management, and running executable files. see [bash variable primer](compciv.org/topics/bash/variables-and-substitution/), [bash evironment variables](gnu.org/software/bash/manual/html_node/Bash-Variables.html), [bash builtin commands](tldp.org/LDP/abs/html/internal.html), and the [shell reference manual](tldp.org/LDP/abs/html/refcards.html). bash (as well as readline) were originally developed by [Brian Fox](wikipedia.org/wiki/Brian_Fox_(computer_programmer)), and then passed to [Chet Ramey](tiswww.case.edu/php/chet/).
:tv:<br>mintty          | a terminal emulator that ships with git-for-windows. adheres to standards on interpreting special control-sequences (of which there are [surprisingly many](xfree86.org/current/ctlseqs.html)), and is fairly simple. does not provide window tabbing. "tty" is short for ["teletype"](wikipedia.org/wiki/Teleprinter). see ["tips on using mintty"](github.com/mintty/mintty/wiki/Tips) and [".minttyrc"](mintty.github.io/mintty.1.html).
:train:<br>readline     | a program that binds command-line-manipulating actions to key-sequences, such as moving the caret to the beginning of the line (Ctrl+A), to the end of the line (Ctrl+E), deleting a word (Ctrl+W), deleting everything before the caret (Ctrl+U), and more, other actions include command-history recall and searching, as well as structured and composable command auto-completion. bindings can be set on the spot using the "bind" command, and defaults can be setup in an [".inputrc"](gnu.org/software/bash/manual/html_node/Readline-Init-File.html) file. you can find a full description of default bindings and actions [here](gnu.org/software/bash/manual/html_node/Bindable-Readline-Commands.html). I have gotten so used to readline key-bindings that I sometimes absentmindedly close browser tabs while trying to delete a word in the search bar, or open the page's html source trying to delete the search line.
:scroll:<br>less        | less is a pager program. it allows you to feed it input from a file or from the output of another command and to quickly scroll through it using mappable key-bindings. you can view its help page with the command "less --help". to quit the pager, press "q". user configurations can be specified in a [".lesskey"](linux.die.net/man/1/lesskey) file.
:pencil2:<br>vim        | vim is a text editor that displays in your terminal window. it has little to no user interface, and leaves all actions to short key-sequences. it is known for having a sharp learning curve (like a wall), but having that when-your-scissors-start-gliding feeling after you climb over it. here's a [good read](csswizardry.com/2014/06/vim-for-people-who-think-things-like-vim-are-weird-and-hard/) advocating for vim. I had a lightbulb moment about vim after learning about keybindings in readline and less: in normal mode, vim uses paging key-bindings identical to those in the less pager (usually with the \<ctrl\> key prepended). that includes (c)d, (c)u, (c)f, (c)b, g, G, j, k, (c)y, and (c)e. it also uses the same mappings to set and jump to (book)marks, and to perform searching (/, n, and N) and file opening (:e). in insert mode, vim follows some movement key-bindings from readline, such as ctrl+w and ctrl+u. in vim, you can open the help menu by going to normal mode (ctrl+c), and then typing ":help", optionally followed by a search topic.
:camera:<br>git         | a version control system that saves incremental changes as snapshots of changed files in their entirety in a local hidden directory as a tree-like structure. I have found git's tutorial-style documentation on [branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) and on [demystifying the reset command](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified) to be incredibly helpful.



## How it looks when I start bash:
![startup](images/startup.PNG)


## How my vim looks:
![vimrc](images/vimrc.PNG)


## My modified "ls -la":
![lsa](images/lsa.PNG)
