#!/usr/bin/env python3
# -*- coding: latin-1 -*- ######################################################
#                                                                              #
# sploitctl.py - fetch, install and search exploit archives from exploit sites #
#                                                                              #
# DESCRIPTION                                                                  #
# Script to fetch, install, update and search exploit archives from well-known #
# sites like packetstormsecurity.com and exploit-db.com.                       #
#                                                                              #
# AUTHORS                                                                      #
# sepehrdad.dev@gmail.com                                                      #
#                                                                              #
#                                                                              #
# PREVIOUS AUTHORS                                                             #
# noptrix@nullsecurity.net                                                     #
# teitelmanevan@gmail.com                                                      #
# nrz@nullsecurity.net                                                         #
# kurobeats@outlook.com                                                        #
#                                                                              #
################################################################################


__organization__: str = "blackarch.org"
__license__: str = "GPLv3"
__version__: str = "3.0.0-beta"  # sploitctl.py version
__project__: str = "sploitctl"

# default exploit base directory
__exploit_path__: str = "/usr/share/exploits"

__decompress__: bool = False
__remove__: bool = False
__max_trds__: int = 4
__useragent__: str = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
__executer__ = None
__chunk_size__: int = 1024
__proxy__: dict = {}
__max_retry__: int = 3

__repo__: dict = {}
__repo_file__: str = ""


def err(string: str) -> None:
    print(colored("[-]", "red", attrs=["bold"]), string, file=sys.stderr)


def warn(string: str) -> None:
    print(colored("[!]", "yellow", attrs=["bold"]), string)


def info(string: str) -> None:
    print(colored("[*]", "blue", attrs=["bold"]), string)


# usage and help
def usage() -> None:
    global __project__
    global __exploit_path__
    global __max_trds__
    global __max_retry__
    __usage__ = "usage:\n\n"
    __usage__ += f"  {__project__} -f <arg> [options] | -u <arg> [options] | -s <arg> [options] | <misc>\n\n"
    __usage__ += "options:\n\n"
    __usage__ += "  -f <num>   - download exploit archives from chosen sites\n"
    __usage__ += "             - ? to list sites\n"
    __usage__ += "  -u <num>   - update exploit archive from chosen installed archive\n"
    __usage__ += "             - ? to list downloaded archives\n"
    __usage__ += "  -d <dir>   - exploits base directory (default: /usr/share/exploits)\n"
    __usage__ += "  -s <regex> - exploits to search using <regex> in base directory\n"
    __usage__ += "  -t <num>   - max parallel downloads (default: 4)\n"
    __usage__ += "  -r <num>   - max retry failed downloads (default: 3)\n"
    __usage__ += "  -A <str>   - set useragent string\n"
    __usage__ += "  -P <str>   - set proxy (format: proto://user:pass@host:port)\n"
    __usage__ += "  -X         - decompress archive\n"
    __usage__ += "  -R         - remove archive after decompression\n\n"
    __usage__ += "misc:\n\n"
    __usage__ += f"  -V         - print version of {__project__} and exit\n"
    __usage__ += "  -H         - print this help and exit\n\n"
    __usage__ += "example:\n\n"
    __usage__ += "  # download and decompress all exploit archives and remove archive\n"
    __usage__ += f"  $ {__project__} -f 0 -XR\n\n"
    __usage__ += "  # download all exploits in packetstorm archive\n"
    __usage__ += f"  $ {__project__} -f 4\n\n"
    __usage__ += "  # list all available exploit archives\n"
    __usage__ += f"  $ {__project__} -f ?\n\n"
    __usage__ += "  # download and decompress all exploits in m00-exploits archive\n"
    __usage__ += f"  $ {__project__} -f 2 -XR\n\n"
    __usage__ += "  # download all exploits archives using 20 threads and 4 retries\n"
    __usage__ += f"  $ {__project__} -r 4 -f 0 -t 20\n\n"
    __usage__ += "  # download lsd-pl-exploits to \"~/exploits\" directory\n"
    __usage__ += f"  $ {__project__} -f 3 -d ~/exploits\n\n"
    __usage__ += "  # download all exploits with using tor socks5 proxy\n"
    __usage__ += f"  $ {__project__} -f 0 -P \"socks5://127.0.0.1:9050\"\n\n"
    __usage__ += "  # download all exploits with using http proxy and noleak useragent\n"
    __usage__ += f"  $ {__project__} -f 0 -P \"http://127.0.0.1:9060\" -A \"noleak\"\n\n"
    __usage__ += "  # list all installed exploits available for download\n"
    __usage__ += f"  $ {__project__} -u ?\n\n"
    __usage__ += "  # update all installed exploits with using http proxy and noleak useragent\n"
    __usage__ += f"  $ {__project__} -u 0 -P \"http://127.0.0.1:9060\" -A \"noleak\" -XR\n\n"
    __usage__ += "notes:\n\n"
    __usage__ += f"  * {__project__} update's id are relative to the installed archives\n"
    __usage__ += "    and are not static, so by installing an exploit archive it will\n"
    __usage__ += "    show up in the update section so always do a -u ? before updating.\n"

    print(__usage__)


# print version
def version() -> None:
    global __project__
    global __version__
    __str_version__ = f"{__project__} v{ __version__}"
    print(__str_version__)


# leet banner, very important
def banner() -> None:
    global __project__
    global __organization__
    __str_banner__ = f"--==[ {__project__} by {__organization__} ]==--\n"
    print(colored(__str_banner__, "red", attrs=["bold"]))


def check_packetstorm(url: str) -> bool:
    global __proxy__
    res = requests.head(url, allow_redirects=True,
                        headers={'User-Agent': __useragent__},
                        proxies=__proxy__)
    return not res.url.endswith("404.html")


def sync_packetstorm_yearly(start: int, end: int, repo: list) -> None:
    for i in range(start, end):
        url = f"https://dl.packetstormsecurity.net/{str(i)[-2:]}12-exploits/{i}-exploits.tgz"
        if url in repo:
            continue
        if check_packetstorm(url):
            repo.append(url)


def sync_packetstorm_monthly(start: int, end: int, year: int, repo: list) -> None:
    for i in range(start, end):
        url = f"https://dl.packetstormsecurity.net/{str(year)[-2:]}{i:02d}-exploits/{str(year)[-2:]}{i:02d}-exploits.tgz"
        if url in repo:
            continue
        if check_packetstorm(url):
            repo.append(url)


# sync packetstorm urls
def sync_packetstorm(update: bool = False) -> None:
    global __repo__
    info("syncing packetstorm repository")
    current_year = int(date.today().strftime("%Y"))
    current_month = int(date.today().strftime("%m"))

    if update:
        sync_packetstorm_monthly(
            10, 13, 1999, __repo__["packetstorm"]["update"])
        for i in range(2000, current_year):
            sync_packetstorm_monthly(
                1, 13, i, __repo__["packetstorm"]["update"])
        sync_packetstorm_monthly(
            1, current_month + 1,
            current_year, __repo__["packetstorm"]["update"])
    else:
        sync_packetstorm_yearly(1999, current_year + 1,
                                __repo__["packetstorm"]["fetch"])
        if current_month < 12:
            sync_packetstorm_monthly(
                1, current_month + 1,
                current_year, __repo__["packetstorm"]["fetch"])


# decompress file
def decompress(infilename: str) -> None:
    filename = os.path.basename(infilename)
    os.chdir(os.path.dirname(infilename))
    archive = None
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
def remove(filename: str) -> None:
    try:
        os.remove(filename)
    except:
        pass


# check if directory exists
def check_dir(dir_name: str) -> None:
    try:
        if os.path.isdir(dir_name):
            return
        else:
            info(f"creating directory {dir_name}")
            os.mkdir(dir_name)
    except Exception as ex:
        err(f"unable to create directory: {str(ex)}")
        exit(-1)


# check if file exists
def check_file(path: str) -> bool:
    return os.path.exists(f"{path}")


# check if proxy is valid using regex
def check_proxy(proxy: dict) -> None:
    try:
        reg = r"^(http|https|socks4|socks5)://([a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@)?[a-z0-9.]+:[0-9]{1,5}$"
        if not re.match(reg, proxy['http']):
            raise ValueError("proxy is malformed")
    except Exception as ex:
        err(f"unable to use proxy: {str(ex)}")
        exit(-1)


# convert string to int
def check_int(string: str) -> int:
    try:
        return int(string)
    except:
        err(f'{string} is not a valid number')
        exit(-1)


# get the lists of installed archives in the base path
def get_installed() -> list:
    available = []
    for _, i in enumerate(__repo__):
        if os.path.isdir(os.path.join(__exploit_path__, i)):
            available.append(i)
    return available


# fetch file from git
def fetch_file_git(url: str, path: str) -> None:
    pygit2.clone_repository(url, path)


# fetch file from http
def fetch_file_http(url: str, path: str) -> None:
    global __proxy__
    rq = requests.get(url, stream=True, headers={
        'User-Agent': __useragent__}, proxies=__proxy__)
    fp = open(path, 'wb')
    for data in rq.iter_content(chunk_size=__chunk_size__):
        fp.write(data)
    fp.close()


# fetch file wrapper
def fetch_file(url: str, path: str) -> None:
    global __decompress__
    global __max_retry__

    for _ in range(0, __max_retry__ + 1):
        try:
            filename = os.path.basename(path)
            check_dir(os.path.dirname(path))

            if check_file(path):
                warn(f"{filename} already exists -- skipping")
            else:
                info(f"downloading {filename}")
                if str(url).startswith('git+'):
                    fetch_file_git(url.replace("git+", ""), path)
                else:
                    fetch_file_http(url, path)
            if __decompress__ and not str(url).startswith('git+'):
                decompress(path)
                if __remove__:
                    remove(path)
            break
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            err(f"Error while downloading {url}: {str(ex)}")
            remove(path)


# wrapper around fetch_file
def fetch(id: int) -> None:
    global __repo__
    global __executer__
    repo_list = list(__repo__.keys())
    try:
        if id > repo_list.__len__():
            raise OverflowError("id is too big")
        elif id < 0:
            raise IndexError("id is too small")

        if (id == 0) or (repo_list[id - 1] == "packetstorm"):
            sync_packetstorm()

        if id == 0:
            for _, i in enumerate(__repo__):
                base_path = f"{__exploit_path__}/{i}"
                check_dir(base_path)
                for _, j in enumerate(__repo__[i]['fetch']):
                    __executer__.submit(
                        fetch_file, j, f"{base_path}/{str(j).split('/')[-1]}")
        else:
            site = repo_list[id - 1]
            base_path = f"{__exploit_path__}/{site}"
            check_dir(base_path)
            for _, i in enumerate(__repo__[site]['fetch']):
                __executer__.submit(
                    fetch_file, i, f"{base_path}/{str(i).split('/')[-1]}")
        __executer__.shutdown(wait=True)
    except Exception as ex:
        err(f"unable to fetch archive: {str(ex)}")


# update git repository
def update_git(name: str, path: str) -> None:
    try:
        os.chdir(path)
        repo = pygit2.repository.Repository(path)
        for remote in repo.remotes:
            if remote.name == "origin":
                remote.fetch()
                remote_master_id = repo.lookup_reference(
                    "refs/remotes/origin/master").target
                merge_result, _ = repo.merge_analysis(remote_master_id)
                if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                    return
                elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                    repo.checkout_tree(repo.get(remote_master_id))
                    try:
                        master_ref = repo.lookup_reference('refs/heads/master')
                        master_ref.set_target(remote_master_id)
                    except KeyError:
                        repo.create_branch(
                            "master", repo.get(remote_master_id))
                    repo.head.set_target(remote_master_id)
                raise AssertionError('unknown state')
            else:
                raise AssertionError('unknown state')
    except Exception as ex:
        err(f"unable to update {name}: {str(ex)}")


# update exploit-db exploits
def update_exploitdb() -> None:
    global __exploit_path__
    global __repo__
    global __executer__
    info("updating exploit-db")
    base_path = f"{__exploit_path__}/exploit-db"
    for _, i in enumerate(__repo__["exploit-db"]["fetch"]):
        path = f"{base_path}/{str(i).split('/')[-1]}"
        if os.path.exists(path):
            name = path.split('/')[-1]
            __executer__.submit(update_git, name, path)
        else:
            __executer__.submit(fetch_file, i, path)


# generic updater for m00-exploits and lsd-pl-exploits
def update_generic(site: str) -> None:
    global __exploit_path__
    global __repo__
    global __executer__
    info(f"updating {site}")
    base_path = f"{__exploit_path__}/{site}"
    repo = __repo__[site]['fetch']

    if "update" in __repo__[site]:
        repo = __repo__[site]["update"]

    if site == "packetstorm":
        sync_packetstorm(update=True)

    for _, i in enumerate(repo):
        path = f"{base_path}/{str(i).split('/')[-1]}"
        if os.path.exists(str(path).split('.')[0]):
            continue
        __executer__.submit(fetch_file, i, path)


# wrapper around update_* functions
def update(id: int) -> None:
    global __executer__
    funcs = []
    installed = get_installed()
    funcs_dict = {
        "exploit-db": [update_exploitdb],
        "packetstorm": [update_generic, "packetstorm"],
        "m00-exploits": [update_generic, "m00-exploits"],
        "lsd-pl-exploits": [update_generic, "lsd-pl-exploits"]
    }
    try:
        if id > installed.__len__():
            raise OverflowError("id is too big")
        elif id < 0:
            raise IndexError("id is too small")

        if id == 0:
            for _, i in enumerate(installed):
                funcs.append(funcs_dict[i])
        else:
            funcs.append(funcs_dict[installed[id - 1]])
        for _, i in enumerate(funcs):
            if i.__len__() == 1:
                i[0]()
            else:
                i[0](i[1])
        __executer__.shutdown(wait=True)
    except Exception as ex:
        err(f"unable to update: {str(ex)}")


# print available sites for archive download
def print_sites(func: callable) -> None:
    global __repo__
    try:
        available = []
        if func.__name__ == "fetch":
            available = __repo__
        elif func.__name__ == "update":
            available = get_installed()
        if available.__len__() <= 0:
            raise EnvironmentError("No archive available")
        info("available exploit sites and archives:\n")
        print("    > 0   - all exploit sites")
        for i, j in enumerate(available):
            print(f"    > {i + 1}   - {j}")
    except Exception as ex:
        err(str(ex))
        exit(-1)


# search exploits directory for regex match
def search(regex: str) -> None:
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


# load repo.json file to __repo__
def load_repo() -> None:
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


# flush __repo__ to disk
def save_repo() -> None:
    global __repo__
    global __repo_file__
    try:
        fp = open(__repo_file__, 'w')
        json.dump(__repo__, fp)
        fp.close()
    except Exception as ex:
        err(f"Error while saving Repo: {str(ex)}")
        exit(-1)


def parse_args(argv: list) -> tuple:
    global __exploit_path__
    global __decompress__
    global __remove__
    global __max_trds__
    global __useragent__
    global __proxy__
    global __max_retry__
    __operation__ = None
    __arg__ = None
    opFlag = 0

    try:
        opts, _ = getopt.getopt(argv[1:], "f:u:s:d:t:r:A:P:VHXDR")

        if opts.__len__() <= 0:
            __operation__ = usage
            return __operation__, None

        for opt, arg in opts:
            if opFlag and re.fullmatch(r"^-([fsu])", opt):
                raise getopt.GetoptError("multiple operations selected")
            if opt == '-f':
                if arg == '?':
                    __operation__ = print_sites
                    __arg__ = fetch
                else:
                    __operation__ = fetch
                    __arg__ = check_int(arg)
                opFlag += 1
            elif opt == '-u':
                if arg == '?':
                    __operation__ = print_sites
                    __arg__ = update
                else:
                    __operation__ = update
                    __arg__ = check_int(arg)
                opFlag += 1
            elif opt == '-s':
                __operation__ = search
                __arg__ = arg
                opFlag += 1
            elif opt == '-d':
                dirname = os.path.abspath(arg)
                check_dir(dirname)
                __exploit_path__ = dirname
            elif opt == '-t':
                __max_trds__ = check_int(arg)
                if __max_trds__ <= 0:
                    raise Exception("threads number can't be less than 1")
            elif opt == '-r':
                __max_retry__ = check_int(arg)
                if __max_retry__ < 0:
                    raise Exception("retry number can't be less than 0")
            elif opt == '-A':
                __useragent__ = arg
            elif opt == '-P':
                if arg.startswith('http://'):
                    __proxy__ = {"http": arg}
                else:
                    __proxy__ = {"http": arg, "https": arg}
                check_proxy(__proxy__)
            elif opt == '-X':
                __decompress__ = True
            elif opt == '-R':
                __remove__ = True
            elif opt == '-V':
                version()
                exit(0)
            elif opt == '-H':
                usage()
                exit(0)
    except getopt.GetoptError as ex:
        err(f"Error while parsing arguments: {str(ex)}")
        warn("-H for help and usage")
        exit(-1)
    except Exception as ex:
        err(f"Error while parsing arguments: {str(ex)}")
        err("WTF?! mount /dev/brain")
        exit(-1)
    return __operation__, __arg__


# controller and program flow
def main(argv: list) -> int:
    global __executer__
    global __max_trds__
    global __repo_file__
    global __exploit_path__
    banner()

    __repo_file__ = f"{os.path.dirname(os.path.realpath(__file__))}/repo.json"

    load_repo()

    __operation__, __args__ = parse_args(argv)

    __executer__ = ThreadPoolExecutor(__max_trds__)

    if __operation__ == None:
        err("no operation selected")
        err("WTF?! mount /dev/brain")
        return -1

    if __args__ == None:
        __operation__()
    else:
        __operation__(__args__)

    __executer__.shutdown()

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
        from concurrent.futures import ThreadPoolExecutor
    except Exception as ex:
        print(f"Error while loading dependencies: {str(ex)}", file=sys.stderr)
        exit(-1)
    sys.exit(main(sys.argv))
