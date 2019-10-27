
# Darcy

"darcy" is how I like to slur the pronunciation of ".\*rc", which is the [fileglob pattern](http://tldp.org/LDP/GNU-Linux-Tools-Summary/html/x11655.htm) for typical standalone [run-configuration files](wikipedia.org/wiki/Configuration_file). Most of the contents of this repo no longer follow that glob ever since the commit where I moved everything to fall under one directory, but I'm keeping the name because I think it has a nice ring to it.

As I said, everything is under one directory, which means less clutter, and easier portability. All you need to do to use my environment is to clone and copy this repo to the directory specified by the environment variable ["XGD\_CONFIG\_HOME"](https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html), which by convention is usually ~/.config/ if set by default. You should source :/git/bashrc in your ~/.bash\_profile file, or whatever is passed as the --init-file argument when invoking bash. You can put a gitconfig-style file in /git/config\_\_local containing your name and email. Similarly, you can put machine-local bash run-config comands in /bash/aliases\_\_local.

I like to mess around and explore things. Sometimes that has led to me messing up things that I don't understand. So what I like about this whole project is that all there is to mess up is my own stuff. I can poke around and tinker to my heart's content. To me, reading about different parts of the terminal environment is like going on a treasure hunt. And while I don't even know what I'm looking for half the time, I enjoy almost every minute of it. At first, the question that always came up in my mind was "why is *<thing that doesn't follow conventions of modern applications>* this way?". And as I explored and learned about different pieces of the bigger picture, I started to see connections and how pieces build on top of, or around each other.

For example, I wondered why vim doesn't save buffers using Ctrl+S by default. As I learned more about vim and started trying to write keymappings, I found out that Ctrl+S is reserved for manual [XON/XOFF flow-control](wikipedia.org/wiki/Software_flow_control) in most terminals, which exists because before terminals were emulated by modern computers, which can scroll through scrollback buffers quite quickly, people needed a mechanism to pause a terminal's output so the operator could actually read it. vim, for the most part, being a superset of VI, followed in VI's footsteps to honor the terminal's [default ownership](https://retrocomputing.stackexchange.com/questions/7263/history-of-ctrl-s-and-ctrl-q-for-flow-control) of that key-sequence. I found that this behaviour could be disabled using the stty (set teletype) command, which allowed me to map the update command in vim to Ctrl+S. As an aside, if there are any hardcore vim users shaking their fists right now saying I'm using vim wrong, I disagree. I think that if you leverage the configurability of a tool to make it work better for yourself, you are doing it exactly right.

If you're wondering why I don't use WSL, it's because when I started using git-for-windows, I had absolutely no idea what was going on, and it was hard for me to do or find worthwhile pretty much anything I saw. I've come a long way since then, and I may look at switching to WSL in the future, but not until I feel like I'm being limited by MinGW.



## A Bird's Eye View

This is a high level view of what I have learned about terminal-related facilities. Because I learned it on my own, the things I have to say are in the words of a beginner, and I may have accidentally gotten something wrong. If you notice anything wrong or that can be improved, please shoot me a message and correct me!

program     | description
----------- | -----------
bash        | a shell based on sh with features from other shells like csh and ksh. shells allow you to interact with your operating system's kernel by providing certain services, and making those callable through a command-line interface. those services include creating and destroying files and directories, writing to and reading from files, performing file processing, and navigating directories, job / process management, and running executable files.
mintty      | a terminal emulator that ships with git-for-windows. adheres to standards (of which there are [surprisingly many](https://www.xfree86.org/current/ctlseqs.html)), and is fairly simple. does not provide tabbing. "tty" is short for ["teletype"](wikipedia.org/wiki/Teleprinter). see ["tips on using mintty"](https://github.com/mintty/mintty/wiki/Tips) and [".minttyrc"](https://mintty.github.io/mintty.1.html).
readline    | a program that binds command-line-manipulating actions to key-sequences, such as moving the caret to the beginning of the line, deleting a word, deleting the whole line, and so on, as well as command history management, and structured, composable command auto-completion.
vim         | vim is a text editor that displays in your terminal window. it has little to no user interface, and leaves all actions to short key-sequences. it is known for having a sharp learning curve (like a wall), but having that when-your-scissors-start-gliding feeling after you climb over it. here's a [good read](https://csswizardry.com/2014/06/vim-for-people-who-think-things-like-vim-are-weird-and-hard/) advocating for vim.



## How it looks when I start bash:
![startup](images/startup.PNG)


## How my vim looks:
![vimrc](images/vimrc.PNG)


## My modified "ls -la":
![lsa](images/lsa.PNG)
