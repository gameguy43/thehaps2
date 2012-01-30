#!/bin/sh
sudo apt-get install postfix vim
cp .procmailrc_sample ~/.procmailrc
echo "adjust the procmailrc"
vim ~/.procmailrc
