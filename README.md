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

  sploitctl -f <arg> [options] | -u <arg> [options] | -s <arg> [options] | <misc>

options:

  -f <num>   - download exploit archives from chosen sites
             - ? to list sites
  -u <num>   - update exploit archive from chosen installed archive
             - ? to list downloaded archives
  -d <dir>   - exploits base directory (default: /usr/share/exploits)
  -s <regex> - exploits to search using <regex> in base directory
  -t <num>   - max parallel downloads (default: 4)
  -r <num>   - max retry failed downloads (default: 3)
  -A <str>   - set useragent string
  -P <str>   - set proxy (format: proto://user:pass@host:port)
  -X         - decompress archive
  -R         - remove archive after decompression

misc:

  -V         - print version of sploitctl and exit
  -H         - print this help and exit

example:

  # download and decompress all exploit archives and remove archive
  $ sploitctl -f 0 -XR

  # download all exploits in packetstorm archive
  $ sploitctl -f 4

  # list all available exploit archives
  $ sploitctl -f ?

  # download and decompress all exploits in m00-exploits archive
  $ sploitctl -f 2 -XR

  # download all exploits archives using 20 threads and 4 retries
  $ sploitctl -r 4 -f 0 -t 20

  # download lsd-pl-exploits to "~/exploits" directory
  $ sploitctl -f 3 -d ~/exploits

  # download all exploits with using tor socks5 proxy
  $ sploitctl -f 0 -P "socks5://127.0.0.1:9050"

  # download all exploits with using http proxy and noleak useragent
  $ sploitctl -f 0 -P "http://127.0.0.1:9060" -A "noleak"

  # list all installed exploits available for download
  $ sploitctl -u ?

  # update all installed exploits with using http proxy and noleak useragent
  $ sploitctl -u 0 -P "http://127.0.0.1:9060" -A "noleak" -XR

notes:

  * sploitctl update's id are relative to the installed archives
    and are not static, so by installing an exploit archive it will
    show up in the update section so always do a -u ? before updating.
```

## Get Involved

You can get in touch with the BlackArch Linux team. Just check out the following:

**Please, send us pull requests!**

**Web:** https://www.blackarch.org/

**Mail:** team@blackarch.org

**IRC:** [irc://irc.freenode.net/blackarch](irc://irc.freenode.net/blackarch)
