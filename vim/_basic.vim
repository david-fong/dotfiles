set t_Co=8
"colorscheme wildcharm
"filetype plugin on
"syntax on
hi Comment ctermfg=darkgrey

set autoindent
set smartindent
set tabstop=3
set softtabstop=3 "use &tabstop
set shiftwidth=0  "use &tabstop
set shiftround    "round when shifting
"set expandtab

set formatoptions=croqlj
set vb t_vb=
set belloff=all
set mouse=a
set clipboard=unnamed
set ignorecase
set smartcase
set incsearch

set title
set splitright
set wildmenu
set wildmode=list:longest,longest:full
set showcmd

autocmd FileType markdown set expandtab tabstop=2 softtabstop=2

if &diff
syntax off
endif
