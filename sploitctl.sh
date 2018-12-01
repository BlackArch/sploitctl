#!/bin/sh
################################################################################
#                                                                              #
# sploitctl.sh - fetch, install and search exploit archives from exploit sites #
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
#                                                                              #
################################################################################

# sploitctl.sh version
VERSION="sploitctl.sh v2.1.7"

# return codes
SUCCESS=0
FAILURE=1

# true / false flags
TRUE=1
FALSE=0

# verbose mode - default: quiet
VERBOSE="/dev/null"

# debug mode - default: off
DEBUG="/dev/null"

# default exploit base directory
EXPLOIT_DIR="/usr/share/exploits"

# exploit subdirectories
EXPLOITDB_DIR="${EXPLOIT_DIR}/exploit-db"
PSTORM_DIR="${EXPLOIT_DIR}/packetstorm"
M00_DIR="${EXPLOIT_DIR}/m00-exploits"
LSDPL_DIR="${EXPLOIT_DIR}/lsd-pl-exploits"

# default base url for packetstorm
PSTORM_URL="https://dl.packetstormsecurity.net/"

# link to m00 exploits archive
M00_URL="https://github.com/BlackArch/m00-exploits/raw/master/m00-exploits.tar.gz"

# link to lsd-pl exploits archive
LSDPL_URL="https://github.com/BlackArch/lsd-pl-exploits/archive/master.zip"

# clean up, delete downloaded archive files (default: on)
CLEAN=$TRUE

# user agent string for curl
USERAGENT='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:63.0) Gecko/20180101 Firefox/63.0'

# browser open url in web search option
BROWSER="xdg-open" # allow for use of user defined default browser

# default url list for web option
URL_FILE="/usr/share/sploitctl/web/url.lst"

# download agent
DLAGENT="curl -k -# -L --create-dirs"


# print error and exit
err()
{
  echo "[-] ERROR: ${@}"

  exit $FAILURE
}


# print warning
warn()
{
  echo "[!] WARNING: ${@}"

  return $SUCCESS
}


# print verbose message
vmsg()
{
  echo "    > ${@}"

  return $SUCCESS
}


# print message
msg()
{
  echo "[+] ${@}"

  return $SUCCESS
}


# delete downloaded archive files
clean()
{
  if [ $CLEAN -eq $TRUE ]
  then
    msg "deleting archive files"
    # Not defined by POSIX (SC2039). Read the commit message for details.
    rm -rf "${EXPLOIT_DIR}"/{*.tar,*.tgz,*.tar.gz,*.tar.bz2,*.tar.xz,*.zip} \
      > $DEBUG 2>&1
    rm -rf packetstorm/{*.tar,*.tgz,*.tar.gz,*.tar.bz2,*.tar.xz,*.zip} \
      > $DEBUG 2>&1
    rm -rf m00/m00-exploits.tar.gz > $DEBUG 2>&1
    rm -rf lsd-pl/lsd-pl-exploits-master > $DEBUG 2>&1
    rm -rf lsd-pl/master.zip > $DEBUG 2>&1
  fi

  return $SUCCESS
}


# search exploit(s) for given search pattern in web sites
search_web()
{
  name="${srch_str}"

  msg "searching '${name}'"

  while read -r;
  do
    # Where REPLY is defined?
    open_browser "${REPLY}" "${name}"
  done < "${URL_FILE}"

  return $SUCCESS
}


# search exploit(s) using given string pattern
search_archive()
{
  msg "searching exploit for '${srch_str}'"

  if [ -d "${EXPLOIT_DIR}" ]
  then
    for i in $(grep -ri --exclude={'*htm*','files.csv'} "${srch_str}" \
      "${EXPLOIT_DIR}" | cut -d ':' -f 1 | sort -u)
    do
      # Could we split ';' ?
      printf "%-80s |   " "${i}" ; grep -m 1 -i "${srch_str}" "${i}"
    done | sort -u
  else
    err "no exploits directory found"
  fi

  return $SUCCESS
}


# open browser for the search
open_browser()
{
  url="${1}"
  name="${2}"

  domain=$(printf "%s" "${url}" | sed 's|\(http://[^/]*/\).*|\1|g')

  vmsg "opening '${domain}' in ${BROWSER}" > $VERBOSE 2>&1
  "${BROWSER}" "${url}${name}"

  return $SUCCESS
}


# extract lsd-pl-exploits archives and do changes if necessary
extract_lsdpl()
{
  vmsg "extracting lsd-pl archive: master.zip" > $VERBOSE 2>&1
  unzip lsd-pl/master.zip -d lsd-pl/ > $DEBUG 2>&1 ||
    warn "failed to extract lsd-pl-exploits ${f}"

  mv lsd-pl/lsd-pl-exploits-master/* lsd-pl/ > $DEBUG 2>&1

  for zip in lsd-pl/*.zip
  do
    unzip "${zip}" -d lsd-pl/ > $DEBUG 2>&1
    rm -rf "${zip}" > $DEBUG 2>&1
  done

  return $SUCCESS
}


# extract m00-exploits archives and do changes if necessary
extract_m00()
{
  vmsg "extracting m00 archive: m00-exploits.tar.gz" > $VERBOSE 2>&1
  tar xfvz m00/*.tar.gz -C m00/ > $DEBUG 2>&1 ||
    warn "failed to extract m00-exploits.tar.gz"
  mv m00/m00-exploits/* m00/
  rmdir m00/m00-exploits > $DEBUG 2>&1

  return $SUCCESS
}


# extract packetstorm archives and do changes if necessary
extract_pstorm()
{
  for f in packetstorm/*.tgz
  do
    vmsg "extracting packetstorm archive: $(echo ${f} |
      sed 's/packetstorm\///')" > $VERBOSE 2>&1
    tar xfvz "${f}" -C packetstorm/ > $DEBUG 2>&1 ||
      warn "failed to extract packetstorm ${f}"
  done

  return $SUCCESS
}


# extract exploit-db archive and do changes if necessary
extract_exploitdb()
{
  return $SUCCESS
}


# extract exploit archives
extract()
{
  echo
  msg "extracting exploit archives"
  echo

  case $site in
    0)
      vmsg "extracting all archives" > $VERBOSE 2>&1
      extract_exploitdb
      extract_pstorm
      extract_m00
      extract_lsdpl
      ;;
    1)
      vmsg "extracting exploit-db archives" > $VERBOSE 2>&1
      extract_exploitdb
      ;;
    2)
      vmsg "extracting packetstorm archives" > $VERBOSE 2>&1
      extract_pstorm
      ;;
    3)
      vmsg "extracting m00-exploits archives" > $VERBOSE 2>&1
      extract_m00
      ;;
    4)
      vmsg "extracting lsd-pl-exploits archives" > $VERBOSE 2>&1
      extract_lsdpl
      ;;

  esac

  return $SUCCESS
}


# update packetstorm archive
update_pstorm()
{
  cd $EXPLOIT_DIR

  today=$(date +%y%m)
  last=$(find . -type d | cut -d '-' -f 1 | tr -d './' | sort -u | tail -1 |
    sed 's/packetstorm//')
  next=$(expr $last + 1)

  for i in $(seq $next $today)
  do
    vmsg "downloading $i-exploits.tgz" > $VERBOSE 2>&1
    $DLAGENT -A "$USERAGENT" -o "packetstorm/$i-exploits.tgz" \
      "$PSTORM_URL/$i-exploits/$i-exploits.tgz" > $DEBUG 2>&1 ||
      err "failed to download packetstorm"
  done

  extract_pstorm

  cd ..

  return $SUCCESS
}


# update exploit-db archive
update_exploitdb()
{
  if [ -f "${EXPLOITDB_DIR}/files_exploits.csv" ]
  then
    cd exploit-db || err "could not change to exploit-db dir"
    #git config user.email "foo@bar"
    #git config user.name "foo bar"
    git stash > $DEBUG 2>&1
    git pull > $DEBUG 2>&1
    cd ..
  fi

  return $SUCCESS
}


# update existing exploit archives
update()
{
  msg "updating exploit archives"
  echo

  case $site in
    0)
      vmsg "updating all exploit archives" > $VERBOSE 2>&1
      update_exploitdb
      update_pstorm
      ;;
    1)
      vmsg "updating exploit-db archive" > $VERBOSE 2>&1
      update_exploitdb
      ;;
    2)
      vmsg "upating packetstorm archive" > $VERBOSE 2>&1
      update_pstorm
      ;;
  esac

  return $SUCCESS
}


# fix file permissions
fix_perms()
{
  echo
  msg "fixing permissions"

  find "${EXPLOIT_DIR}" -type d -exec chmod 755 {} \; > $DEBUG 2>&1
  find "${EXPLOIT_DIR}" -type f -exec chmod 644 {} \; > $DEBUG 2>&1
  chown -R root:root ${EXPLOIT_DIR} > $DEBUG 2>&1

  return $SUCCESS
}


# download lsd-pl exploit archives from our github repository
fetch_lsdpl()
{
  vmsg "downloading lsd-pl-exploits" > $VERBOSE 2>&1

  $DLAGENT -A "$USERAGENT" "${LSDPL_URL}" -o "lsd-pl/master.zip" \
    > $DEBUG 2>&1 || err "failed to download lsd-pl-exploits"

  return $SUCCESS
}


# download m00 exploit archives from our github repository. some greets here to
# crash-x darkeagle and my old homies :(
fetch_m00()
{
  vmsg "downloading m00-exploits" > $VERBOSE 2>&1

  $DLAGENT -A "$USERAGENT" "${M00_URL}" -o "m00/m00-exploits.tar.gz" \
    > $DEBUG 2>&1 || err "failed to download m00-exploits"

  return $SUCCESS
}


# download exploit archives from packetstorm
# TODO: dirty hack here. make it better
fetch_pstorm()
{
  # enough for the next 83 years ;)
  cur_year=$(date +%y)
  y=0

  vmsg "downloading archives from packetstorm" > $VERBOSE 2>&1

  while [ "${y}" -le "${cur_year}" ]
  do
    for m in {1..12}
    do
      if [ "${y}" -lt 10 ]
      then
        year="0${y}"
      else
        year="${y}"
      fi
      if [ "${m}" -lt 10 ]
      then
        month="0${m}"
      else
        month="${m}"
      fi
      vmsg "downloading ${year}${month}-exploits.tgz" > $VERBOSE 2>&1
      $DLAGENT -A "$USERAGENT" \
        "${PSTORM_URL}/${year}${month}-exploits/${year}${month}-exploits.tgz" \
        -o "packetstorm/${year}${month}-exploits.tgz" > $DEBUG 2>&1 ||
        err "failed to download packetstorm"
    done
    y=$((y+1))
  done

  return $SUCCESS
}


# download exploit archives from exploit-db
fetch_exploitdb()
{
  vmsg "downloading archive from exploit-db" > $VERBOSE 2>&1

  if [ ! -f "${EXPLOITDB_DIR}/files.csv" ]
  then
    git clone https://github.com/offensive-security/exploit-database.git \
      exploit-db > $DEBUG 2>&1
  fi

  return $SUCCESS
}


# download exploit archives from chosen sites
fetch()
{
  msg "downloading exploit archives"
  echo

  case $site in
    0)
      fetch_exploitdb
      fetch_pstorm
      fetch_m00
      fetch_lsdpl
      ;;
    1)
      fetch_exploitdb
      ;;
    2)
      fetch_pstorm
      ;;
    3)
      fetch_m00
      ;;
    4)
      fetch_lsdpl
      ;;
  esac

  return $SUCCESS
}


# create parent exploit dir and cd into it
make_exploit_dir()
{
  if [ ! -d "${EXPLOIT_DIR}" ]
  then
    if ! mkdir "${EXPLOIT_DIR}" > $DEBUG 2>&1
    then
      err "failed to create ${EXPLOIT_DIR}"
    fi
  fi

  cd $EXPLOIT_DIR

  return $SUCCESS
}


# checks for old exploit dir: /var/exploits
check_old_expl_dir()
{
  if [ -d "/var/exploits" ]
  then
    warn "old directory \"/var/exploits\" exists!"
    printf "  > delete old directory? [y/N]: "
    read answer
    if [ "${answer}" = "y" ]
    then
      vmsg "deleting \"/var/exploits\" ..." > $VERBOSE 2>&1
      rm -rf "/var/exploits"
    else
      return $SUCCESS
    fi
  fi

  return $SUCCESS
}


# usage and help
usage()
{
  echo "usage:"
  echo ""
  echo "  sploitctl.sh -f <arg> | -u <arg> | -s <arg> | -e <arg> [options] | <misc>"
  echo ""
  echo "options:"
  echo ""
  echo "  -f <num>  - download and extract exploit archives from chosen sites"
  echo "            - ? to list sites"
  echo "  -u <num>  - update exploit archive from chosen site - ? to list sites"
  echo "  -s <str>  - exploit to search using <str> in ${EXPLOIT_DIR}"
  echo "  -w <str>  - exploit to search in web exploit site"
  echo "  -e <dir>  - exploits base directory (default: /usr/share/exploits)"
  echo "  -b <url>  - give a new base url for packetstorm"
  echo "              (default: http://dl.packetstormsecurity.com/)"
  echo "  -l <file> - give a new base path/file for website list option"
  echo "              (default: /usr/share/sploitctl/web/url.lst)"
  echo "  -c        - do not delete downloaded archive files"
  echo "  -v        - verbose mode (default: off)"
  echo "  -d        - debug mode (default: off)"
  echo ""
  echo "misc:"
  echo ""
  echo "  -V        - print version of sploitctl and exit"
  echo "  -H        - print this help and exit"

  exit $SUCCESS
}


# leet banner, very important
banner()
{
  echo "--==[ sploitctl.sh by blackarch.org ]==--"
  echo

  return $SUCCESS
}


# check chosen website
check_site()
{
  if [ "${site}" = "?" ]
  then
    msg "available exploit sites"
    vmsg "0   - all exploit sites"
    vmsg "1   - exploit-db.com"
    vmsg "2   - packetstormsecurity.org"
    vmsg "3   - m00-exploits"
    vmsg "4   - lsd-pl-exploits"
    exit $SUCCESS
  elif [ "${site}" -lt 0 ] || [ "${site}" -gt 4 ]
  then
    err "unknown exploit site"
  fi

  return $SUCCESS
}


# check argument count
check_argc()
{
  if [ ${#} -lt 1 ]
  then
    err "-H for help and usage"
  fi

  return $SUCCESS
}


# check if requimsg arguments were selected
check_args()
{
  msg "checking arguments"

  if [ -z "${job}" ]
  then
    err "choose -f, -u or -s"
  fi

  if [ "${job}" = "search_web" ] && [ ! -f "${URL_FILE}" ]
  then
    err "failed to get url file for web searching - try -l <file>"
  fi

  return $SUCCESS
}


# check to ensure the script is run as root/sudo
check_uid()
{
  if [ "$(id -u)" != "0" ]
  then
    err "This script must be run as root. Later hater."
  fi
}


# parse command line options
get_opts()
{
  while getopts f:u:s:w:e:b:l:cvdVH flags
  do
    case "${flags}" in
      f)
        job="fetch"
        site="${OPTARG}"
        check_site
        ;;
      u)
        job="update"
        site="${OPTARG}"
        check_site
        ;;
      s)
        job="search_archive"
        srch_str="${OPTARG}"
        ;;
      w)
        job="search_web"
        srch_str="${OPTARG}"
        ;;
      e)
        EXPLOIT_DIR="${OPTARG}"
        ;;
      b)
        PSTORM_URL="${OPTARG}"
        ;;
      l)
        URL_FILE="${OPTARG}"
        ;;
      c)
        CLEAN=$FALSE
        ;;
      v)
        VERBOSE="/dev/stdout"
        ;;
      d)
        DEBUG="/dev/stdout"
        ;;
      V)
        echo "${VERSION}"
        exit $SUCCESS
        ;;
      H)
        usage
        ;;
      *)
        err "WTF?! mount /dev/brain"
        ;;
    esac
  done

  return $SUCCESS
}


# controller and program flow
main()
{
  banner
  check_argc "${@}"
  get_opts "${@}"
  check_args "${@}"
  check_uid

  case "${job}" in
    "fetch")
      check_old_expl_dir
      make_exploit_dir
      fetch
      extract
      fix_perms
      clean
      ;;
    "update")
      update
      fix_perms
      clean
      ;;
    "search_archive")
      search_archive
      ;;
    "search_web")
      search_web
      ;;
    *)
      err "WTF?! mount /dev/brain"
  esac

  msg "game over"

  return $SUCCESS
}


# program start
main "${@}"


# EOF
