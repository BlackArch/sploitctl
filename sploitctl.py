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

    for i in range(1999, int(current_year) + 1):
        url = f"http://dl.packetstormsecurity.net/{str(i)[-2:]}12-exploits/{i}-exploits.tgz"
        if url in __repo__["packetstormsecurity.org"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstormsecurity.org"].append(url)
    if int(current_month) is 12:
        return
    for i in range(1, int(current_month) + 1):
        url = f"http://dl.packetstormsecurity.net/{str(current_year)[-2:]}{i:02d}-exploits/{str(current_year)[-2:]}{i:02d}-exploits.tgz"
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
        info(f"decompressing {filename} completed")
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
def fetch_http(url, path):
    rq = requests.get(url, stream=True, headers={
        'User-Agent': __useragent__})
    fp = open(path, 'wb')
    for data in rq.iter_content(chunk_size=__chunk_size__):
        fp.write(data)
    fp.close()


# fetch file wrapper
def fetch(url, path):
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
            fetch_http(url, path)
        info(f"downloading {filename} completed")
    except KeyboardInterrupt:
        pass
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
    except Exception as ex:
        err(f"unable to update archive: {str(ex)}")
    finally:
        unblock_stdout()


def load_repo():
    global __repo__
    repo_file = f"{os.path.dirname(os.path.realpath(__file__))}/repo.json"
    try:
        if not os.path.isfile(repo_file):
            raise FileNotFoundError("Repo file not found")
        fp = open(repo_file, 'r')
        __repo__ = json.load(fp)
        fp.close()
    except Exception as ex:
        err(f"Error while loading Repo: {str(ex)}")
        exit(-1)


def save_repo():
    global __repo__
    repo_file = f"{os.path.dirname(os.path.realpath(__file__))}/repo.json"
    try:
        fp = open(repo_file, 'w')
        json.dump(__repo__, fp)
        fp.close()
    except Exception as ex:
        err(f"Error while saving Repo: {str(ex)}")
        exit(-1)


def parse_args(argv):
    pass


def main(argv):
    banner()

    load_repo()

    parse_args(argv)

    save_repo()
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
