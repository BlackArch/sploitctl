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
__executer__ = None
__chunk_size__ = 1024

__repo__ = {}
__repo_file__ = None


def err(string):
    print(colored("[-]", "red", attrs=["bold"]), string, file=sys.stderr)


def warn(string):
    print(colored("[!]", "yellow", attrs=["bold"]), string)


def info(string):
    print(colored("[*]", "blue", attrs=["bold"]), string)


# usage and help
def usage():
    __usage__ = "usage:\n\n"
    __usage__ += f"  {__project__} -f <arg> [options] | -s <arg> [options] | <misc>\n\n"
    __usage__ += "options:\n\n"
    __usage__ += "  -f <num>   - download exploit archives from chosen sites\n"
    __usage__ += "             - ? to list sites\n"
    __usage__ += f"  -d <dir>   - exploits base directory (default: {__exploit_path__})\n"
    __usage__ += "  -s <regex> - exploits to search using <regex> in base directory\n\n"
    __usage__ += "misc:\n\n"
    __usage__ += "  -X         - decompress archive\n"
    __usage__ += "  -R         - remove archive after decompression\n"
    __usage__ += f"  -V         - print version of {__project__} and exit\n"
    __usage__ += "  -H         - print this help and exit\n\n"

    print(__usage__)


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
    info("syncing packetstorm archives")
    current_year = date.today().strftime("%Y")
    current_month = date.today().strftime("%m")

    for i in range(1999, int(current_year) + 1):
        url = f"http://dl.packetstormsecurity.com/{str(i)[-2:]}12-exploits/{i}-exploits.tgz"
        if url in __repo__["packetstormsecurity.org"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstormsecurity.org"].append(url)
    if int(current_month) is 12:
        return
    for i in range(1, int(current_month) + 1):
        url = f"http://dl.packetstormsecurity.com/{str(current_year)[-2:]}{i:02d}-exploits/{str(current_year)[-2:]}{i:02d}-exploits.tgz"
        if url in __repo__["packetstormsecurity.org"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstormsecurity.org"].append(url)


# decompress file
def decompress(infilename):
    filename = os.path.basename(infilename)
    os.chdir(os.path.dirname(infilename))
    archive = None
    if __decompress__ is False:
        return
    try:
        info(f"decompressing {filename}")
        if re.fullmatch(r"^.*\.(tgz|tar.gz)$", filename.lower()):
            archive = tarfile.open(filename)
        elif re.fullmatch(r"^.*\.(zip)$", filename.lower()):
            archive = zipfile.ZipFile(filename)
        else:
            raise TypeError("file type not supported")
        archive.extractall()
        archive.close()
    except Exception as ex:
        err(f'Error while decompressing {filename}: {str(ex)}')


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
            return
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
    pygit2.clone_repository(str(url).replace('git+', ''), path)


# fetch file from http
def fetch_file_http(url, path):
    rq = requests.get(url, stream=True, headers={
        'User-Agent': __useragent__})
    fp = open(path, 'wb')
    for data in rq.iter_content(chunk_size=__chunk_size__):
        fp.write(data)
    fp.close()


# fetch file wrapper
def fetch_file(url, path):
    global __decompress__
    try:
        filename = os.path.basename(path)
        direc = os.path.dirname(path)
        check_dir(direc)

        if check_file(path):
            return warn(f"{filename} already exists -- skipping")

        info(f"downloading {filename}")
        if str(url).startswith('git+'):
            fetch_file_git(url.replace("git+", ""), path)
        else:
            fetch_file_http(url, path)
            if __decompress__:
                decompress(path)
                if __remove__:
                    remove(path)
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        err(f"Error while downloading {url}: {str(ex)}")
        remove(path)


def fetch(id):
    global __repo__
    global __executer__
    repo_list = list(__repo__.keys())
    try:
        if id > repo_list.__len__():
            raise OverflowError("id is too big")
        elif id < 0:
            raise IndexError("id is too small")

        sync_packetstorm()

        if id is 0:
            for _, i in enumerate(__repo__):
                base_path = f"{__exploit_path__}/{i}"
                check_dir(base_path)
                for _, j in enumerate(__repo__[i]):
                    __executer__.submit(
                        fetch_file, j, f"{base_path}/{str(j).split('/')[-1]}")
        else:
            site = repo_list[id - 1]
            base_path = f"{__exploit_path__}/{site}"
            check_dir(base_path)
            for _, i in enumerate(__repo__[site]):
                __executer__.submit(
                    fetch_file, i, f"{base_path}/{str(i).split('/')[-1]}")
        __executer__.shutdown(wait=True)
    except Exception as ex:
        err(f"unable to fetch archive: {str(ex)}")


# update git repository
def update_git(name, path):
    try:
        block_stdout()
        os.chdir(path)
        repo = pygit2.repository.Repository(path)
        repo.stash(repo.default_signature)
        repo.remotes['origin'].fetch()
    except Exception as ex:
        err(f"unable to update archive: {str(ex)}")
    finally:
        unblock_stdout()


def update_packetstorm():
    pass


def update(id):
    pass


# search exploits directory for regex match
def search(regex):
    global __exploit_path__
    count = 0
    try:
        for root, _, files in os.walk(__exploit_path__):
            for f in files:
                if re.match(regex, f):
                    info(f"exploit found: {os.path.join(root, f)}")
                    count += 1
        if count == 0:
            err("exploit not found")
    except:
        pass


def load_repo():
    global __repo__
    global __repo_file__

    try:
        if not os.path.isfile(__repo_file__):
            raise FileNotFoundError("Repo file not found")
        fp = open(__repo_file__, 'r')
        __repo__ = json.load(fp)
        fp.close()
    except Exception as ex:
        err(f"Error while loading Repo: {str(ex)}")
        exit(-1)


def save_repo():
    global __repo__
    global __repo_file__
    try:
        fp = open(__repo_file__, 'w')
        json.dump(__repo__, fp)
        fp.close()
    except Exception as ex:
        err(f"Error while saving Repo: {str(ex)}")
        exit(-1)


def parse_args(argv):
    global __exploit_path__
    global __decompress__
    __operation__ = None
    __arg__ = None

    try:
        opts, _ = getopt.getopt(argv[1:], "f:u:s:d:VHXDR")

        for opt, arg in opts:
            if opt == '-f':
                __operation__ = fetch
                __arg__ = to_int(arg)
            elif opt == '-u':
                __operation__ = update
                __arg__ = to_int(arg)
            elif opt == '-s':
                __operation__ = search
                __arg__ = arg
            elif opt == '-d':
                dirname = os.path.abspath(arg)
                check_dir(dirname)
                __exploit_path__ = dirname
            elif opt == '-X':
                __decompress__ = True
            elif opt == '-V':
                version()
                exit(0)
            elif opt == '-H':
                usage()
                exit(0)
    except Exception as ex:
        err(f"Error while parsing arguments: {str(ex)}")
        err("WTF?! mount /dev/brain")
        exit(-1)
    return __operation__, __arg__


# controller and program flow
def main(argv):
    global __executer__
    global __max_trds__
    global __repo_file__
    banner()

    __repo_file__ = f"{os.path.dirname(os.path.realpath(__file__))}/repo.json"

    load_repo()

    __executer__ = ThreadPoolExecutor(__max_trds__)
    __operation__, __args__ = parse_args(argv)

    if __operation__ == None:
        err("no operation selected")
        return -1

    if __args__ == None:
        __operation__()
    else:
        __operation__(__args__)

    __executer__.shutdown()

    save_repo()

    info("game over")

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
        import json
        from datetime import date
        from termcolor import colored
        from shutil import copyfileobj, rmtree, chown
        from concurrent.futures import ThreadPoolExecutor
    except Exception as ex:
        print(f"Error while loading dependencies: {str(ex)}", file=sys.stderr)
        exit(-1)
    sys.exit(main(sys.argv))
