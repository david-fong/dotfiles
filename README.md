
# Darcy

"darcy" is how I like to slur the pronunciation of ".\*rc", which is the fileglob pattern for typical standalone run-configuration files. Most of the contents of this repo no longer follow that glob ever since the commit where I moved everything to fall under one directory, but I'm keeping the name because I think it has a nice ring to it.

As I said, everything is under one directory, which means less clutter, and easier portability. All you need to do to use my environment is to clone and copy this repo to the directory specified by the environment variable "XGD\_CONFIG\_HOME", which by default should be ~/.config/. If XGD\_CONFIG\_HOME does not exist, set it to whatever you'd like (although the default is recommended). You should source /git/bashrc in your ~/.bash\_profile file (or whatever is specified in the --init-file argument when invoking bash). You can put a gitconfig-style file in /git/config\_\_local containing your name and email. Similarly, you can put machine-local bash run-config comands in /bash/aliases\_\_local.

I like to mess around and explore things. Sometimes that has led to me messing up things that I don't understand. So what I like about this whole project is that all there is to mess up is my own stuff. I am free to mess around, poke around, and tinker to my heart's content. To me, reading about different parts of the terminal environment is like going on a treasure hunt- except half the time I don't even know what I'm looking for. To me, that is half the fun! At first, the question that always came up in my mind was "why is *x* this way?". And as I explored and learned about different pieces of the bigger picture, I started to see connections and how pieces build on top of, or around each other. For example, I wondered why vim doesn't save buffers using Ctrl+S by default. As I learned more about vim and started trying to write keymappings, I found out that Ctrl+S is reserved for XON/XOFF flow-control in most terminals, which exists because before terminals were emulated by modern computers, which can scroll through scrollback buffers quite quickly, people needed a mechanism to pause a terminal's output so the operator could actually read it. vim, for the most part, being a superset of VI, followed in VI's footsteps to honor the terminal's default owndership of that key-sequence. I found that this behaviour could be disabled using the stty (set teletype) command, which allowed me to map the update command in vim to Ctrl+S. As an aside, if there are any hardcore vim users shaking their fists right now saying I'm using vim wrong, I disagree. I think that if you leverage the configurability of a tool to make it work better for yourself, you are doing it exactly right.



## A Bird's Eye View





## How it looks when I start bash:
![startup](images/startup.PNG)


## How my vim looks:
![vimrc](images/vimrc.PNG)


## My modified "ls -la":
![lsa](images/lsa.PNG)
