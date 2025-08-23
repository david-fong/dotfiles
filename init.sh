cp ~/.config/bash/profile ~/.profile
[ -f ~/.bashrc ] && mv ~/.bashrc ~/.bashrc~
[ -f ~/.bash_profile ] && mv ~/.bash_profile ~/.bash_profile~

mkdir -p ~/c
mkdir -p ~/c/m

# https://superuser.com/a/215506
mkdir -p -m700 ~/.ssh
[ -f ~/.ssh/config ] || echo 'AddKeysToAgent=yes' > ~/.ssh/config
chmod 600 ~/.ssh/*
chmod 644 ~/.ssh/*.pub

[ -d /etc ] && mkdir -p /etc/brave/policies/managed/
[ -d /etc ] && cp ~/.config/etc/brave/policies/managed/GroupPolicy.json /etc/brave/policies/managed/
