#!/bin/sh
sudo apt-get install postfix vim procmail
cp .procmailrc_sample ~/.procmailrc
echo "adjust the procmailrc"
vim ~/.procmailrc
