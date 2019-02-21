## Description

Script to fetch, install, update and search exploit archives from well-known
sites like packetstormsecurity.org and exploit-db.com.

In the latest version of the Blackarch Linux it has been added to
**/usr/share/exploits** directory.

## Installation

`pacman -S sploitctl`

## Usage

```
[ noptrix@blackarch-dev ~/blackarch/repos/sploitctl ]$ ./sploitctl.sh -H
--==[ sploitctl.sh by blackarch.org ]==--

usage:

  sploitctl.sh -f <arg> | -u <arg> | -s <arg> | -e <arg> [options] | <misc>

options:

  -f <num>  - download and extract exploit archives from chosen sites
            - ? to list sites
  -u <num>  - update exploit archive from chosen site
            - ? to list sites
  -s <str>  - exploit to search using <str> in /usr/share/exploits
  -w <str>  - exploit to search in web exploit site
  -e <dir>  - exploits base directory (default: /usr/share/exploits)
  -b <url>  - give a new base url for packetstorm
              (default: http://dl.packetstormsecurity.com/)
  -l <file> - give a new base path/file for website list option
              (default: /usr/share/sploitctl/web/url.lst)
  -c        - do not delete downloaded archive files
  -v        - verbose mode (default: off)
  -d        - debug mode (default: off)

misc:

  -V        - print version of sploitctl and exit
  -H        - print this help and exit
```

## Get Involved

You can get in touch with the BlackArch Linux team. Just check out the following:

**Please, send us pull requests!**

**Web:** https://www.blackarch.org/

**Mail:** team@blackarch.org

**IRC:** [irc://irc.freenode.net/blackarch](irc://irc.freenode.net/blackarch)
