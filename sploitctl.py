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

# load dependencies
import sys
import os
import getopt
import re
import tarfile
import zipfile
import json
import csv
from datetime import date
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    import pygit2
    from termcolor import colored
except Exception as ex:
    print(f"Error while loading dependencies: {str(ex)}", file=sys.stderr)
    exit(-1)


ORGANIZATION: str = "blackarch.org"
LICENSE: str = "GPLv3"
VERSION: str = "3.0.3"  # sploitctl.py version
PROJECT: str = "sploitctl"

exploit_path: str = "/usr/share/exploits"  # default exploit base directory
exploit_repo: dict = {}

decompress_archive: bool = False
remove_archive: bool = False
max_trds: int = 4
useragent_string: str = f"{PROJECT}/{VERSION}"
parallel_executer = None
proxy_settings: dict = {}
max_retry: int = 3

CHUNK_SIZE: int = 1024
REPO_FILE: str = f"{os.path.dirname(os.path.realpath(__file__))}/repo.json"


def err(string: str) -> None:
    print(colored("[-]", "red", attrs=["bold"]), string, file=sys.stderr)


def warn(string: str) -> None:
    print(colored("[!]", "yellow", attrs=["bold"]), string)


def info(string: str) -> None:
    print(colored("[*]", "blue", attrs=["bold"]), string)


# usage and help
def usage() -> None:
    global PROJECT
    global exploit_path
    global max_trds
    global max_retry
    str_usage = "usage:\n\n"
    str_usage += f"  {PROJECT} -f <arg> [options] | -u <arg> [options] | -s <arg> [options] | <misc>\n\n"
    str_usage += "options:\n\n"
    str_usage += "  -f <num>   - download exploit archives from chosen sites\n"
    str_usage += "             - ? to list sites\n"
    str_usage += "  -u <num>   - update exploit archive from chosen installed archive\n"
    str_usage += "             - ? to list downloaded archives\n"
    str_usage += "  -d <dir>   - exploits base directory (default: /usr/share/exploits)\n"
    str_usage += "  -s <regex> - exploits to search using <regex> in base directory\n"
    str_usage += "  -t <num>   - max parallel downloads (default: 4)\n"
    str_usage += "  -r <num>   - max retry failed downloads (default: 3)\n"
    str_usage += "  -A <str>   - set useragent string\n"
    str_usage += "  -P <str>   - set proxy (format: proto://user:pass@host:port)\n"
    str_usage += "  -X         - decompress archive\n"
    str_usage += "  -R         - remove archive after decompression\n\n"
    str_usage += "misc:\n\n"
    str_usage += f"  -V         - print version of {PROJECT} and exit\n"
    str_usage += "  -H         - print this help and exit\n\n"
    str_usage += "example:\n\n"
    str_usage += "  # download and decompress all exploit archives and remove archive\n"
    str_usage += f"  $ {PROJECT} -f 0 -XR\n\n"
    str_usage += "  # download all exploits in packetstorm archive\n"
    str_usage += f"  $ {PROJECT} -f 4\n\n"
    str_usage += "  # list all available exploit archives\n"
    str_usage += f"  $ {PROJECT} -f ?\n\n"
    str_usage += "  # download and decompress all exploits in m00-exploits archive\n"
    str_usage += f"  $ {PROJECT} -f 2 -XR\n\n"
    str_usage += "  # download all exploits archives using 20 threads and 4 retries\n"
    str_usage += f"  $ {PROJECT} -r 4 -f 0 -t 20\n\n"
    str_usage += "  # download lsd-pl-exploits to \"~/exploits\" directory\n"
    str_usage += f"  $ {PROJECT} -f 3 -d ~/exploits\n\n"
    str_usage += "  # download all exploits with using tor socks5 proxy\n"
    str_usage += f"  $ {PROJECT} -f 0 -P \"socks5://127.0.0.1:9050\"\n\n"
    str_usage += "  # download all exploits with using http proxy and noleak useragent\n"
    str_usage += f"  $ {PROJECT} -f 0 -P \"http://127.0.0.1:9060\" -A \"noleak\"\n\n"
    str_usage += "  # list all installed exploits available for download\n"
    str_usage += f"  $ {PROJECT} -u ?\n\n"
    str_usage += "  # update all installed exploits with using http proxy and noleak useragent\n"
    str_usage += f"  $ {PROJECT} -u 0 -P \"http://127.0.0.1:9060\" -A \"noleak\" -XR\n\n"
    str_usage += "notes:\n\n"
    str_usage += f"  * {PROJECT} update's id are relative to the installed archives\n"
    str_usage += "    and are not static, so by installing an exploit archive it will\n"
    str_usage += "    show up in the update section so always do a -u ? before updating.\n"

    print(str_usage)


# print version
def version() -> None:
    global PROJECT
    global VERSION
    print(f"{PROJECT} v{ VERSION}")


# leet banner, very important
def banner() -> None:
    global PROJECT
    global ORGANIZATION
    str_banner = f"--==[ {PROJECT} by {ORGANIZATION} ]==--\n"
    print(colored(str_banner, "red", attrs=["bold"]))


def check_packetstorm(url: str) -> bool:
    global proxy_settings
    res = requests.head(url, allow_redirects=True,
                        headers={'User-Agent': useragent_string},
                        proxies=proxy_settings)
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
        url = f"https://dl.packetstormsecurity.net/{str(year)[-2:]}{i:02d}-exploits/{str(year)[-2:] if year < 2020 else str(year)}{i:02d}-exploits.tgz"
        if url in repo:
            continue
        if check_packetstorm(url):
            repo.append(url)


# sync packetstorm urls
def sync_packetstorm(update: bool = False) -> None:
    global exploit_repo
    info("syncing packetstorm repository")
    current_year = int(date.today().strftime("%Y"))
    current_month = int(date.today().strftime("%m"))

    if update:
        sync_packetstorm_monthly(
            10, 13, 1999, exploit_repo["packetstorm"]["update"])
        for i in range(2000, current_year):
            sync_packetstorm_monthly(
                1, 13, i, exploit_repo["packetstorm"]["update"])
        sync_packetstorm_monthly(
            1, current_month + 1,
            current_year, exploit_repo["packetstorm"]["update"])
    else:
        sync_packetstorm_yearly(1999, current_year + 1,
                                exploit_repo["packetstorm"]["fetch"])
        if current_month < 12:
            sync_packetstorm_monthly(
                1, current_month + 1,
                current_year, exploit_repo["packetstorm"]["fetch"])


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
    for _, i in enumerate(exploit_repo):
        if os.path.isdir(os.path.join(exploit_path, i)):
            available.append(i)
    return available


# fetch file from git
def fetch_file_git(url: str, path: str) -> None:
    pygit2.clone_repository(url, path)


# fetch file from http
def fetch_file_http(url: str, path: str) -> None:
    global proxy_settings
    global max_retry

    partpath: str = f"{path}.part"
    headers: dict = {'User-Agent': useragent_string}

    if os.path.isfile(partpath):
        size: int = os.stat(partpath).st_size
        headers["Range"] = f'bytes={size}-'

    for _ in range(max_retry):
        rq: requests.Response = requests.get(
            url, stream=True, headers=headers, proxies=proxy_settings)

        if rq.status_code == 404:
            raise FileNotFoundError("host returned 404")
        elif rq.status_code not in [200, 206]:
            time.sleep(5)
            continue

        mode: str = "ab" if rq.status_code == 206 else "wb"
        with open(partpath, mode) as fp:
            for data in rq.iter_content(chunk_size=CHUNK_SIZE):
                fp.write(data)
        os.rename(partpath, path)
        break


# fetch file wrapper
def fetch_file(url: str, path: str) -> None:
    global decompress_archive

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
        if decompress_archive and not str(url).startswith('git+'):
            decompress(path)
            if remove_archive:
                remove(path)
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        err(f"Error while downloading {url}: {str(ex)}")
        remove(path)


# wrapper around fetch_file
def fetch(id: int) -> None:
    global exploit_repo
    global parallel_executer
    repo_list = list(exploit_repo.keys())
    try:
        if id > repo_list.__len__():
            raise OverflowError("id is too big")
        elif id < 0:
            raise IndexError("id is too small")

        if (id == 0) or (repo_list[id - 1] == "packetstorm"):
            sync_packetstorm()

        if id == 0:
            for _, i in enumerate(exploit_repo):
                base_path = f"{exploit_path}/{i}"
                check_dir(base_path)
                for _, j in enumerate(exploit_repo[i]['fetch']):
                    parallel_executer.submit(
                        fetch_file, j, f"{base_path}/{str(j).split('/')[-1]}")
        else:
            site = repo_list[id - 1]
            base_path = f"{exploit_path}/{site}"
            check_dir(base_path)
            for _, i in enumerate(exploit_repo[site]['fetch']):
                parallel_executer.submit(
                    fetch_file, i, f"{base_path}/{str(i).split('/')[-1]}")
        parallel_executer.shutdown(wait=True)
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
    global exploit_path
    global exploit_repo
    global parallel_executer
    info("updating exploit-db")
    base_path = f"{exploit_path}/exploit-db"
    for _, i in enumerate(exploit_repo["exploit-db"]["fetch"]):
        path = f"{base_path}/{str(i).split('/')[-1]}"
        if os.path.exists(path):
            name = path.split('/')[-1]
            parallel_executer.submit(update_git, name, path)
        else:
            parallel_executer.submit(fetch_file, i, path)


# generic updater for m00-exploits and lsd-pl-exploits
def update_generic(site: str) -> None:
    global exploit_path
    global exploit_repo
    global parallel_executer
    info(f"updating {site}")
    base_path = f"{exploit_path}/{site}"
    repo = exploit_repo[site]['fetch']

    if "update" in exploit_repo[site]:
        repo = exploit_repo[site]["update"]

    if site == "packetstorm":
        sync_packetstorm(update=True)

    for _, i in enumerate(repo):
        path = f"{base_path}/{str(i).split('/')[-1]}"
        if os.path.exists(str(path).split('.')[0]):
            continue
        parallel_executer.submit(fetch_file, i, path)


# wrapper around update_* functions
def update(id: int) -> None:
    global parallel_executer
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
        parallel_executer.shutdown(wait=True)
    except Exception as ex:
        err(f"unable to update: {str(ex)}")


# print available sites for archive download
def print_sites(func: callable) -> None:
    global exploit_repo
    try:
        available = []
        if func.__name__ == "fetch":
            available = exploit_repo
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


def search_exploitdb(regex: str, dir: str) -> list:
    exploits_list = [f"{dir}/files_exploits.csv",
                     f"{dir}/files_shellcodes.csv"]
    found = []

    try:
        for exploit in exploits_list:
            fp = open(exploit)
            next(fp)
            for row in csv.reader(fp):
                if re.match(regex, row[2], re.IGNORECASE):
                    found.append(f"{dir}/{row[1]}")
    except:
        pass
    return found


# search exploits directory for regex match
def search(regex: str) -> None:
    global exploit_path
    count = 0
    try:
        for root, dirs, files in os.walk(exploit_path, topdown=True):
            if "exploitdb" in dirs:
                for exploit in search_exploitdb(regex, os.path.join(root, "exploitdb")):
                    info(f"exploit found: {exploit}")
                    count += 1
                dirs[:] = [d for d in dirs if d not in "exploitdb"]
            for f in files:
                if re.match(regex, f, re.IGNORECASE):
                    info(f"exploit found: {os.path.join(root, f)}")
                    count += 1
        if count == 0:
            err("exploit not found")
    except:
        pass


# load repo.json file to exploit_repo
def load_repo() -> None:
    global exploit_repo
    global REPO_FILE

    try:
        if not os.path.isfile(REPO_FILE):
            raise FileNotFoundError("Repo file not found")
        fp = open(REPO_FILE, 'r')
        exploit_repo = json.load(fp)
        fp.close()
    except Exception as ex:
        err(f"Error while loading Repo: {str(ex)}")
        exit(-1)


# flush exploit_repo to disk
def save_repo() -> None:
    global exploit_repo
    global REPO_FILE
    try:
        fp = open(REPO_FILE, 'w')
        json.dump(exploit_repo, fp)
        fp.close()
    except Exception as ex:
        err(f"Error while saving Repo: {str(ex)}")
        exit(-1)


def parse_args(argv: list) -> tuple:
    global exploit_path
    global decompress_archive
    global remove_archive
    global max_trds
    global useragent_string
    global proxy_settings
    global max_retry
    function = None
    arguments = None
    opFlag = 0

    try:
        opts, _ = getopt.getopt(argv[1:], "f:u:s:d:t:r:A:P:VHXDR")

        if opts.__len__() <= 0:
            function = usage
            return function, None

        for opt, arg in opts:
            if opFlag and re.fullmatch(r"^-([fsu])", opt):
                raise getopt.GetoptError("multiple operations selected")
            if opt == '-f':
                if arg == '?':
                    function = print_sites
                    arguments = fetch
                else:
                    function = fetch
                    arguments = check_int(arg)
                opFlag += 1
            elif opt == '-u':
                if arg == '?':
                    function = print_sites
                    arguments = update
                else:
                    function = update
                    arguments = check_int(arg)
                opFlag += 1
            elif opt == '-s':
                function = search
                arguments = arg
                opFlag += 1
            elif opt == '-d':
                dirname = os.path.abspath(arg)
                check_dir(dirname)
                exploit_path = dirname
            elif opt == '-t':
                max_trds = check_int(arg)
                if max_trds <= 0:
                    raise Exception("threads number can't be less than 1")
            elif opt == '-r':
                max_retry = check_int(arg)
                if max_retry < 0:
                    raise Exception("retry number can't be less than 0")
            elif opt == '-A':
                useragent_string = arg
            elif opt == '-P':
                if arg.startswith('http://'):
                    proxy_settings = {"http": arg}
                else:
                    proxy_settings = {"http": arg, "https": arg}
                check_proxy(proxy_settings)
            elif opt == '-X':
                decompress_archive = True
            elif opt == '-R':
                remove_archive = True
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
    return function, arguments


# controller and program flow
def main(argv: list) -> int:
    global parallel_executer
    global max_trds
    global REPO_FILE
    global exploit_path
    banner()

    load_repo()

    function, arguments = parse_args(argv)

    parallel_executer = ThreadPoolExecutor(max_trds)

    if function == None:
        err("no operation selected")
        err("WTF?! mount /dev/brain")
        return -1

    if function in (fetch, update):
        check_dir(exploit_path)

    if arguments == None:
        function()
    else:
        function(arguments)

    parallel_executer.shutdown()

    save_repo()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
