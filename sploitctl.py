#!/usr/bin/env python3
# -*- coding: latin-1 -*- ######################################################
#                                                                              #
# sploitctl.py - fetch, install and search exploit archives from exploit sites #
#                                                                              #
# DESCRIPTION                                                                  #
# Script to fetch, install, update and search exploit archives from well-known #
# sites like packetstormsecurity.org and exploit-db.com.                       #
#                                                                              #
# AUTHORS                                                                      #
# noptrix@nullsecurity.net                                                     #
# teitelmanevan@gmail.com                                                      #
# nrz@nullsecurity.net                                                         #
# kurobeats@outlook.com                                                        #
# sepehrdad.dev@gmail.com                                                      #
#                                                                              #
################################################################################


__organization__ = "blackarch.org"
__license__ = "GPLv3"
__version__ = "3.0.0-beta"  # sploitctl.py version
__project__ = "sploitctl"

# default exploit base directory
__exploit_path__ = "/usr/share/exploits"

__decompress__ = True
__remove__ = True
__max_trds__ = 5
__useragent__ = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
__no_confirm__ = False
__executer__ = None
__chunk_size__ = 1024

__repo__ = {
    "exploit-db": [
        "git+https://github.com/offensive-security/exploitdb.git",
        "git+https://github.com/offensive-security/exploitdb-bin-sploits.git"
    ],
    "m00-exploits": [
        "https://github.com/BlackArch/m00-exploits/raw/master/m00-exploits.tar.gz"
    ],
    "lsd-pl-exploits": [
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/aix.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/bsd.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/hp.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/irix.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/jvm.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/linux.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/other.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/sco.zip",
        "https://github.com/BlackArch/lsd-pl-exploits/raw/master/solaris.zip"
    ],  # packetstormsecurity is precomputed yearly
    "packetstormsecurity.org": [
        "http://dl.packetstormsecurity.net/9912-exploits/1999-exploits.tgz",
        "http://dl.packetstormsecurity.net/0012-exploits/2000-exploits.tgz",
        "http://dl.packetstormsecurity.net/0112-exploits/2001-exploits.tgz",
        "http://dl.packetstormsecurity.net/0212-exploits/2002-exploits.tgz",
        "http://dl.packetstormsecurity.net/0312-exploits/2003-exploits.tgz",
        "http://dl.packetstormsecurity.net/0412-exploits/2004-exploits.tgz",
        "http://dl.packetstormsecurity.net/0512-exploits/2005-exploits.tgz",
        "http://dl.packetstormsecurity.net/0612-exploits/2006-exploits.tgz",
        "http://dl.packetstormsecurity.net/0712-exploits/2007-exploits.tgz",
        "http://dl.packetstormsecurity.net/0812-exploits/2008-exploits.tgz",
        "http://dl.packetstormsecurity.net/0912-exploits/2009-exploits.tgz",
        "http://dl.packetstormsecurity.net/1012-exploits/2010-exploits.tgz",
        "http://dl.packetstormsecurity.net/1112-exploits/2011-exploits.tgz",
        "http://dl.packetstormsecurity.net/1212-exploits/2012-exploits.tgz",
        "http://dl.packetstormsecurity.net/1312-exploits/2013-exploits.tgz",
        "http://dl.packetstormsecurity.net/1412-exploits/2014-exploits.tgz",
        "http://dl.packetstormsecurity.net/1512-exploits/2015-exploits.tgz",
        "http://dl.packetstormsecurity.net/1612-exploits/2016-exploits.tgz",
        "http://dl.packetstormsecurity.net/1712-exploits/2017-exploits.tgz",
        "http://dl.packetstormsecurity.net/1812-exploits/2018-exploits.tgz"
    ]
}


def err(string):
    print(colored("[-]", "red", attrs=["bold"]) +
          f" {string}", file=sys.stderr)


def warn(string):
    print(colored("[!]", "yellow", attrs=["bold"]) + f" {string}")


def info(string):
    print(colored("[*]", "blue", attrs=["bold"]) + f" {string}")


def success(string):
    print(colored("[+]", "green", attrs=["bold"]) + f" {string}")


# usage and help
def usage():
    print("usage")


# print version
def version():
    __str_version__ = f"{__project__} v{ __version__}"
    print(__str_version__)


# block stdout
def block_stdout():
    sys.stdout = open(os.devnull, 'w')


# unblock stdout
def unblock_stdout():
    sys.stdout = sys.__stdout__


# leet banner, very important
def banner():
    __str_banner__ = f"--==[ {__project__} by {__organization__} ]==--\n"
    print(colored(__str_banner__, "red", attrs=["bold"]))


# sync packetstorm urls
def sync_packetstorm():
    global __repo__
    current_year = date.today().strftime("%Y")
    current_month = date.today().strftime("%m")
    for i in range(1999, int(current_year)):
        url = f"http://dl.packetstormsecurity.net/{str(i)[-2:]}12-exploits/{i}-exploits.tgz"
        if url in __repo__["packetstorm.org"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstorm.org"].append(url)
    for i in range(1, int(current_month) + 1):
        url = f"http://dl.packetstormsecurity.net/{str(current_year)[-2:]}{i:02d}-exploits/{str(current_year)[-2:]}{i:02d}-exploits.tgz"
        if url in __repo__["packetstorm.org"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstorm.org"].append(url)


# decompress file
def decompress(infilename):
    filename = os.path.basename(infilename)
    os.chdir(os.path.dirname(infilename))
    archive = None
    if __decompress__ == False:
        return
    try:
        info(f"decompressing {filename}")
        if re.fullmatch(r"^.*\.(tgz)$", filename.lower()):
            archive = tarfile.open(filename)
        elif re.fullmatch(r"^.*\.(zip)$", filename.lower()):
            archive = zipfile.ZipFile(filename)
        else:
            return -1
        archive.extractall()
        archive.close()
        info(f"decompressing {filename} completed")
    except Exception as ex:
        err(f'Error while decompressing {filename}: {str(ex)}')
        return -1


# remove file and ignore errors
def remove(filename):
    try:
        os.remove(filename)
    except:
        pass


# check if directory exists
def check_dir(dir_name):
    try:
        if os.path.isdir(dir_name):
            pass
        else:
            info(f"creating directory {dir_name}")
            os.mkdir(dir_name)
    except Exception as ex:
        err(f"unable to change base directory: {str(ex)}")
        exit(-1)


# check if file exists
def check_file(path):
    return os.path.isfile(f"{path}")


# convert string to int
def to_int(string):
    try:
        return int(string)
    except:
        err(f'{string} is not a valid number')
        exit(-1)


# fetch file from git
def fetch_file_git(url, path):
    try:
        pygit2.clone_repository(str(url).replace('git+', ''), path)
    except Exception as ex:
        err(f"Error while downloading {url}: {str(ex)}")
        remove(path)


# fetch file
def fetch_file(url, path):
    filename = os.path.basename(path)
    direc = os.path.dirname(path)
    check_dir(direc)
    try:
        if check_file(path):
            warn(f"{filename} already exists -- skipping")
        else:
            info(f"downloading {filename}")
            if str(url).startswith('git+'):
                fetch_file_git(url.replace("git+", ""), path)
            else:
                chunk_size = 1024
                rq = requests.get(url, stream=True, headers={
                                  'User-Agent': __useragent__})
                fp = open(path, 'wb')
                for data in rq.iter_content(chunk_size=chunk_size):
                    fp.write(data)
                fp.close()
            info(f"downloading {filename} completed")
        if str(url).startswith('git+'):
            pass
        elif decompress(path) != -1:
            remove(path)
    except KeyboardInterrupt:
        return
    except Exception as ex:
        err(f"Error while downloading {url}: {str(ex)}")
        remove(path)


# update git repository
def update_git(name, path):
    info(f"updating {name}")
    try:
        block_stdout()
        os.chdir(path)
        repo = pygit2.repository.Repository(path)
        repo.stash(repo.default_signature)
        repo.remotes['origin'].fetch()
        unblock_stdout()
    except Exception as ex:
        unblock_stdout()
        err(f"unable to update archive: {str(ex)}")


def main(argv):
    banner()

    return 0


if __name__ == "__main__":
    try:
        # load dependencies
        import sys
        import os
        import getopt
        import requests
        import re
        import tarfile
        import zipfile
        import pygit2
        from datetime import date
        from termcolor import colored
        from shutil import copyfileobj, rmtree, chown
        from concurrent.futures import ThreadPoolExecutor
    except Exception as ex:
        print(f"Error while loading dependencies: {str(ex)}", file=sys.stderr)
        exit(-1)
    sys.exit(main(sys.argv))
