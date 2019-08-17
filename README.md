## Description

Script to fetch, install, update and search exploit archives from well-known
sites like packetstormsecurity.org and exploit-db.com.

In the latest version of the Blackarch Linux it has been added to
**/usr/share/exploits** directory.

## Installation

`pacman -S sploitctl`

## Usage

```
[ noptrix@blackarch-dev ~/blackarch/repos/sploitctl ]$ sploitctl -H
--==[ sploitctl by blackarch.org ]==--

usage:

  sploitctl -f <arg> [options] | -s <arg> [options] | <misc>

options:

  -f <num>   - download exploit archives from chosen sites
             - ? to list sites
  -d <dir>   - exploits base directory (default: /usr/share/exploits)
  -s <regex> - exploits to search using <regex> in base directory
  -t <num>   - max parallel downloads (default: 5)

misc:

  -A         - set useragent string
  -P         - set proxy (format: proto://user:pass@host:port)
  -X         - decompress archive
  -R         - remove archive after decompression
  -V         - print version of sploitctl and exit
  -H         - print this help and exit
```

## Get Involved

You can get in touch with the BlackArch Linux team. Just check out the following:

**Please, send us pull requests!**

**Web:** https://www.blackarch.org/

**Mail:** team@blackarch.org

**IRC:** [irc://irc.freenode.net/blackarch](irc://irc.freenode.net/blackarch)
