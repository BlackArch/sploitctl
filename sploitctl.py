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

__decompress__ = False
__remove__ = False
__max_trds__ = 4
__useragent__ = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
__executer__ = None
__chunk_size__ = 1024
__proxy__ = {}

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
    __usage__ += f"  {__project__} -f <arg> [options] | -u <arg> [options] | -s <arg> [options] | <misc>\n\n"
    __usage__ += "options:\n\n"
    __usage__ += "  -f <num>   - download exploit archives from chosen sites\n"
    __usage__ += "             - ? to list sites\n"
    __usage__ += "  -u <num>   - update exploit archive from chosen site\n"
    __usage__ += "             - ? to list sites\n"
    __usage__ += f"  -d <dir>   - exploits base directory (default: {__exploit_path__})\n"
    __usage__ += "  -s <regex> - exploits to search using <regex> in base directory\n"
    __usage__ += f"  -t <num>   - max parallel downloads (default: {__max_trds__})\n\n"
    __usage__ += "misc:\n\n"
    __usage__ += "  -A <str>   - set useragent string\n"
    __usage__ += "  -P <str>   - set proxy (format: proto://user:pass@host:port)\n"
    __usage__ += "  -X         - decompress archive\n"
    __usage__ += "  -R         - remove archive after decompression\n"
    __usage__ += f"  -V         - print version of {__project__} and exit\n"
    __usage__ += "  -H         - print this help and exit\n"

    print(__usage__)


# print version
def version():
    __str_version__ = f"{__project__} v{ __version__}"
    print(__str_version__)


# leet banner, very important
def banner():
    __str_banner__ = f"--==[ {__project__} by {__organization__} ]==--\n"
    print(colored(__str_banner__, "red", attrs=["bold"]))


# sync packetstorm urls
def sync_packetstorm():
    global __repo__
    info("syncing packetstormsecurity.com archives")
    current_year = date.today().strftime("%Y")
    current_month = date.today().strftime("%m")

    for i in range(1999, int(current_year) + 1):
        url = f"http://dl.packetstormsecurity.com/{str(i)[-2:]}12-exploits/{i}-exploits.tgz"
        if url in __repo__["packetstormsecurity.com"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstormsecurity.com"].append(url)
    if int(current_month) == 12:
        return
    for i in range(1, int(current_month) + 1):
        url = f"http://dl.packetstormsecurity.com/{str(current_year)[-2:]}{i:02d}-exploits/{str(current_year)[-2:]}{i:02d}-exploits.tgz"
        if url in __repo__["packetstormsecurity.com"]:
            continue
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __repo__["packetstormsecurity.com"].append(url)


# decompress file
def decompress(infilename):
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


# check if proxy is valid using regex
def check_proxy(proxy):
    try:
        reg = r"^(http|https|socks4|socks5)://([a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+@)?[a-z0-9.]+:[0-9]{1,5}$"
        if not re.match(reg, proxy['http']):
            raise ValueError("proxy is malformed")
    except Exception as ex:
        err(f"unable to use proxy: {str(ex)}")
        exit(-1)


# convert string to int
def to_int(string):
    try:
        return int(string)
    except:
        err(f'{string} is not a valid number')
        exit(-1)


# get the lists of installed archives in the base path
def get_installed():
    available = []
    for _, i in enumerate(__repo__):
        if os.path.isdir(os.path.join(__exploit_path__, i)):
            available.append(i)
    return available


# fetch file from git
def fetch_file_git(url, path):
    pygit2.clone_repository(str(url).replace('git+', ''), path)


# fetch file from http
def fetch_file_http(url, path):
    global __proxy__
    rq = requests.get(url, stream=True, headers={
        'User-Agent': __useragent__}, proxies=__proxy__)
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
            warn(f"{filename} already exists -- skipping")
        else:
            info(f"downloading {filename}")
            if str(url).startswith('git+'):
                fetch_file_git(url.replace("git+", ""),
                               path.replace(".git", ""))
            else:
                fetch_file_http(url, path)
        if __decompress__ and not str(url).startswith('git+'):
            decompress(path)
            if __remove__:
                remove(path)
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        err(f"Error while downloading {url}: {str(ex)}")
        remove(path)


# wrapper around fetch filed
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

        if id == 0:
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
        os.chdir(path)
        repo = pygit2.repository.Repository(path)
        repo.remotes['origin'].fetch()
    except Exception as ex:
        err(f"unable to update {name}: {str(ex)}")


# update packetstorm exploits
def update_packetstorm():
    global __exploit_path__
    global __repo__
    global __executer__
    info("updating packetstormsecurity.com")
    packetstorm_repo = []
    current_year = date.today().strftime("%Y")
    current_month = date.today().strftime("%m")

    for year in range(1999, int(current_year) + 1):
        for month in range(1, int(current_month) + 1):
            url = f"http://dl.packetstormsecurity.com/{str(year)[-2:]}{month:02d}-exploits/{str(year)[-2:]}{month:02d}-exploits.tgz"
            packetstorm_repo.append(url)

    dirs = [str(x[0]).split('/')[-1]
            for x in os.walk(f"{__exploit_path__}/packetstormsecurity.com")]

    for _, d in enumerate(dirs):
        url = f"http://dl.packetstormsecurity.com/{d}/{d}.tgz"
        if url in packetstorm_repo:
            packetstorm_repo.remove(url)
    base_path = f"{__exploit_path__}/packetstormsecurity.com"
    for _, url in enumerate(packetstorm_repo):
        res = requests.head(url, allow_redirects=True)
        if res.url != url and res.url.endswith("404.html"):
            continue
        __executer__.submit(
            fetch_file, url, f"{base_path}/{str(url).split('/')[-1]}")


# update exploit-db exploits
def update_exploitdb():
    global __exploit_path__
    global __repo__
    global __executer__
    info("updating exploit-db")
    base_path = f"{__exploit_path__}/exploit-db"
    for _, i in enumerate(__repo__["exploit-db"]):
        if os.path.exists(f"{base_path}/{i}"):
            __executer__.submit(update_git, i, f"{base_path}/{i}")
        else:
            __executer__.submit(fetch_file_git, i, f"{base_path}/{i}")


# generic updater for m00-exploits and lsd-pl-exploits
def update_generic(site):
    global __exploit_path__
    global __repo__
    global __executer__
    info(f"updating {site}")
    base_path = f"{__exploit_path__}/{site}"
    for _, i in enumerate(__repo__[site]):
        path = f"{base_path}/{str(i).split('/')[-1]}"
        if os.path.exists(str(path).split('.')[0]):
            continue
        __executer__.submit(
            fetch_file, i, path)


# wrapper around update_* functions
def update(id):
    funcs = []
    installed = get_installed()
    funcs_dict = {
        "exploit-db": [update_exploitdb],
        "packetstormsecurity.com": [update_packetstorm],
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
    except Exception as ex:
        err(f"unable to update: {str(ex)}")


# print available sites for archive download
def print_sites(func):
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


# load repo.json file to __repo__
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


# flush __repo__ to disk
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
    global __remove__
    global __max_trds__
    global __useragent__
    global __proxy__
    __operation__ = None
    __arg__ = None
    opFlag = 0

    try:
        opts, _ = getopt.getopt(argv[1:], "f:u:s:d:t:A:P:VHXDR")

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
                    __arg__ = to_int(arg)
                opFlag += 1
            elif opt == '-u':
                if arg == '?':
                    __operation__ = print_sites
                    __arg__ = update
                else:
                    __operation__ = update
                    __arg__ = to_int(arg)
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
                __max_trds__ = to_int(arg)
                if __max_trds__ <= 0:
                    raise Exception("threads number can't be less than 1")
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
def main(argv):
    global __executer__
    global __max_trds__
    global __repo_file__
    global __exploit_path__
    banner()

    __repo_file__ = f"{os.path.dirname(os.path.realpath(__file__))}/repo.json"

    load_repo()

    __executer__ = ThreadPoolExecutor(__max_trds__)
    __operation__, __args__ = parse_args(argv)

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
        from shutil import copyfileobj, rmtree, chown
        from concurrent.futures import ThreadPoolExecutor
    except Exception as ex:
        print(
            f"Error while loading dependencies: {str(ex)}", file=sys.stderr)
        exit(-1)
    sys.exit(main(sys.argv))
