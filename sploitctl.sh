#!/bin/sh
################################################################################
#                                                                              #
# sploitctl.sh - fetch, install and search exploit archives from exploit sites #
#                                                                              #
# FILE                                                                         #
# sploitctl.sh                                                                 #
#                                                                              #
# DATE                                                                         #
# 2013-12-04                                                                   #
#                                                                              #
# DESCRIPTION                                                                  #
# This script can fetch/install, update and search exploit archives from       #
# well-known sites like packetstormsecurity.org and exploit-db.com.            #
#                                                                              #
# AUTHORS                                                                      #
# noptrix@nullsecurity.net                                                     #
# archey@riseup.net                                                            #
# teitelmanevan@gmail.com                                                      #
# nrz@nullsecurity.net                                                         #
#                                                                              #
# TODO                                                                         #
# - add progress bar for downloading and extracting exploits                   #
# - implement update() routine (makes sense only for packetstorm)              #
# - implement checksum for archives (only download if tarball changed)         #
################################################################################


# sploitctl.sh version
VERSION="sploitctl.sh v1.0"

# true / false
FALSE="0"
TRUE="1"

# return codes
SUCCESS="1337"
FAILURE="31337"

# verbose mode - default: quiet
VERBOSE="/dev/null"

# debug mode - default: off
DEBUG="/dev/null"

# exploit base directory
EXPLOIT_DIR="/usr/share/exploits"

# link to exploit-db's exploit archive
XPLOITDB_URL="http://www.exploit-db.com/archive.tar.bz2"

# base url for packetstorm
PSTORM_URL="http://dl.packetstormsecurity.com/"

# link to m00 exploits archive
M00_URL="https://github.com/BlackArch/m00-exploits/raw/master/m00-exploits.tar.gz"

# clean up, delete downloaded archive files (default: on)
CLEAN=1

# user agent string for curl
USERAGENT="blackarch/${VERSION}"

# browser open url in web search option
BROWSER="firefox"

# default url list for web option
URL_FILE="/usr/share/sploitctl/web/url.lst"

# use colors
COLORS=1

# print line in blue
blue()
{
    msg="${*}"

    if [ ${COLORS} -eq 1 ]
    then
        echo "`tput setaf 4``tput bold`${msg}`tput sgr0`"
    else
        echo "${msg}"
    fi

    return ${SUCCESS}
}


# print line in yellow
yellow()
{
    msg="${*}"

    if [ ${COLORS} -eq 1 ]
    then
        echo "`tput setaf 3``tput bold`${msg}`tput sgr0`"
    else
        echo "${msg}"
    fi

    return ${SUCCESS}
}


# print line in green
green()
{
    msg="${*}"

    if [ ${COLORS} -eq 1 ]
    then
        echo "`tput setaf 2``tput bold`${msg}`tput sgr0`"
    else
        echo "${msg}"
    fi

    return ${SUCCESS}
}


# print line in red
red()
{
    msg="${*}"

    if [ ${COLORS} -eq 1 ]
    then
        echo "`tput setaf 1``tput bold`${msg}`tput sgr0`"
    else
        echo "${msg}"
    fi

    return ${SUCCESS}
}


# print warning
warn()
{
    red "[!] WARNING: ${*}"

    return ${SUCCESS}
}


# print error and exit
err()
{
    red "[-] ERROR: ${*}"
    exit ${FAILURE}

    return ${SUCCESS}
}


# delete downloaded archive files
clean()
{
    if [ ${CLEAN} -eq 1 ]
    then
        blue "[*] deleting archive files" > ${VERBOSE} 2>&1
        rm -rf ${EXPLOIT_DIR}/{*.tar,*.tgz,*.tar.gz,*.tar.bz2} > ${DEBUG} 2>&1
    fi

    return ${SUCCESS}
}


# search exploit(s) for given search pattern. currently exploit-db only.
search_db()
{
    blue "[*] searching exploit for '${srch_str}'"

    if [ -d "${EXPLOIT_DIR}" ]
    then
        green "  -> searching in exploit-db" > ${VERBOSE} 2>&1
        grep -i "${srch_str}" "${EXPLOIT_DIR}/exploit-db/files.csv" \
            2> /dev/null | cut -d ',' -f 2-4 | tr -s ',' ' ' |
        sed -e "s/platforms/\/exploit-db/g"

        green "  -> searching in packetstorm" > ${VERBOSE} 2>&1
        grep -ri --exclude='*htm*' "${srch_str}" "${EXPLOIT_DIR}/packetstorm/" \
            2> /dev/null | grep "/packetstorm" | cut -d '/' -f 3-

        green "  -> searching in m00-exploits" > ${VERBOSE} 2>&1
        grep -ir "${srch_str}" "${EXPLOIT_DIR}/m00-exploits" 2> /dev/null
    else
        err "no exploit-db directory found"
    fi

    return ${SUCCESS}
}

# open browser for the search
open_browser()
{
    url="${1}"
    name="${2}"

    domain=`printf "%s" "${url}" | sed 's|\(http://[^/]*/\).*|\1|g'`

    green "  -> opening '${domain}' in ${BROWSER}" > ${VERBOSE} 2>&1
    "${BROWSER}" "${url}${name}"

    return "${SUCCESS}"
}

# search exploit(s) for given search pattern in web sites
search_web()
{
    name=${srch_str}

    blue "[*] searching '${name}'"

    while read -r;
    do
        open_browser "${REPLY}" "${name}"
    done < "${URL_FILE}"

    return "${SUCCESS}"
}


# extract m00-exploits archives and do changes if necessary
extract_m00()
{
    green "  -> extracting m00-exploits.tar.gz ..." > ${VERBOSE} 2>&1
    tar xfvz m00-exploits.tar.gz > ${DEBUG} 2>&1 ||
      warn "failed to extract m00-exploits ${f}"

    return ${SUCCESS}
}


# extract packetstorm archives and do changes if necessary
extract_pstorm()
{
    for f in *.tgz
    do
        green "  -> extracting ${f} ..." > ${VERBOSE} 2>&1
        tar xfvz ${f} -C "${pstorm_dir}/" > ${DEBUG} 2>&1 ||
            warn "failed to extract packetstorm ${f}"
    done

    return ${SUCCESS}
}


# extract exploit-db archive and do changes if necessary
extract_xploitdb()
{
#    green "  -> extracting archive.tar.bz2 ..." > ${VERBOSE} 2>&1

#    bunzip2 -f archive.tar.bz2 > ${DEBUG} 2>&1 ||
#        err "failed to extract exploit-db"
#    tar xfv archive.tar > ${DEBUG} 2>&1 ||
#        warn "failed to extract exploit-db"

#    mv platforms/* ${xploitdb_dir} > ${DEBUG} 2>&1
#    mv files.csv ${xploitdb_dir} > ${DEBUG} 2>&1

#    rm -rf platforms > ${DEBUG} 2>&1

    blue "[*] fixing permissions"

    find ${xploitdb_dir} -type f -exec chmod 640 {} \; > ${DEBUG} 2>&1

    return ${SUCCESS}
}


# extract exploit archives
extract()
{
    blue "[*] extracting exploit archives"

    case ${site} in
        0)
            extract_xploitdb
            extract_pstorm
            extract_m00
            ;;
        1)
            #green "  -> extracting exploit-db archives ..." > ${VERBOSE} 2>&1
            extract_xploitdb
            ;;
        2)
            green "  -> extracting packetstorm archives ..." > ${VERBOSE} 2>&1
            extract_pstorm
            ;;
        3)
            green "  -> extracting m00-exploits archives ..." > ${VERBOSE} 2>&1
            extract_m00
            ;;
    esac

    return ${SUCCESS}
}


# download m00 exploit archives from our github repository. some greets here to
# crash-x darkeagle and my old homies :(
fetch_m00()
{
    green "  -> downloading m00-exploits from github ..." > ${VERBOSE} 2>&1

    curl -# -A "${USERAGENT}" -L -O ${M00_URL} > ${DEBUG} 2>&1 ||
        err "failed to download m00-exploits"

    return ${SUCCESS}
}


# download exploit archives from packetstorm
fetch_pstorm()
{
    # enough for the next 90 years ;)
    cur_year=`date +%Y | sed 's/.*20//'`
    y=0

    green "  -> downloading archives from packetstorm ..." > ${VERBOSE} 2>&1

    while [ ${y} -le ${cur_year} ]
    do
        for m in {1..12}
        do
            if [ ${y} -lt 10 ]
            then
                year="0${y}"
            else
                year="${y}"
            fi
            if [ ${m} -lt 10 ]
            then
                month="0${m}"
            else
                month="${m}"
            fi
            green "  -> downloading ${year}${month}-exploits.tgz ..." \
                > ${VERBOSE} 2>&1
            curl -# -A "${USERAGENT}" -O \
                "${PSTORM_URL}/${year}${month}-exploits/${year}${month}-exploits.tgz" \
                > ${DEBUG} 2>&1 || err "failed to download packetstorm"
        done
        y=`expr ${y} + 1`
    done

    return ${SUCCESS}
}


# download exploit archives from exploit-db
fetch_xploitdb()
{
    green "  -> downloading archive from exploit-db ..." > ${VERBOSE} 2>&1

    if [ ! -f "${xploitdb_dir}/files.csv" ]
    then
        git clone https://github.com/offensive-security/exploit-database.git \
            exploit-db > ${DEBUG} 2>&1
    else
        cd ${xploitdb_dir}
        git pull > ${DEBUG} 2>&1
        cd ..
    fi

    #curl -# -A "${USERAGENT}" -O ${XPLOITDB_URL}  > ${DEBUG} 2>&1 ||
    #    err "failed to download exploit-db"

    return ${SUCCESS}
}


# download exploit archives from chosen sites
fetch()
{
    blue "[*] downloading exploit archives"

    if [ "${site}" = "0" -o "${site}" = "1" ]
    then
        fetch_xploitdb
    fi
    if [ "${site}" = "0" -o "${site}" = "2" ]
    then
        fetch_pstorm
    fi
    if [ "${site}" = "0" -o "${site}" = "3" ]
    then
        fetch_m00
    fi

    return ${SUCCESS}
}


# define exploit dirs for each site
make_exploit_dirs()
{
    xploitdb_dir="${EXPLOIT_DIR}/exploit-db"
    pstorm_dir="${EXPLOIT_DIR}/packetstorm"
    m00_dir="${EXPLOIT_DIR}/m00-exploits"

    if [ ! -d ${EXPLOIT_DIR} ]
    then
        if ! mkdir ${EXPLOIT_DIR} > ${DEBUG} 2>&1
        then
            err "failed to create ${EXPLOIT_DIR}"
        fi
    fi

    if [ ! -d ${xploitdb_dir} ]
    then
         mkdir ${xploitdb_dir} > ${DEBUG} 2>&1 ||
            err "failed to create ${xploitdb_dir}"
    fi

    if [ ! -d ${pstorm_dir} ]
    then
         mkdir ${pstorm_dir} > ${DEBUG} 2>&1 ||
            err "failed to create ${pstorm_dir}"
    fi

    if [ ! -d ${m00_dir} ]
    then
         mkdir ${m00_dir} > ${DEBUG} 2>&1 ||
            err "failed to create ${m00_dir}"
    fi

    cd "${EXPLOIT_DIR}"

    return ${SUCCESS}
}


# checks for old exploit dir: /var/exploits
check_old_expl_dir()
{
    if [ -d "/var/exploits" ]
    then
        warn "old directory \"/var/exploits\" exists!"
        printf "`tput setaf 2``tput bold`  -> delete old directory?`tput sgr0`"
        printf "`tput setaf 2``tput bold` [y/N]:`tput sgr0` "
        read answer
        if [ "${answer}" = "y" ]
        then
            green " -> deleting \"/var/exploits\" ..."
            rm -rf "/var/exploits"
        else
            return ${SUCCESS}
        fi
    fi

    return ${SUCCESS}
}


# usage and help
usage()
{
    echo "usage:"
    echo ""
    echo "  sploitctl.sh -f <arg> | -s <arg> [options] | <misc>"
    echo ""
    echo "options:"
    echo ""
    echo "  -f <num>    - download and extract exploit archives from chosen"
    echo "                websites - ? to list sites"
    echo "  -s <str>    - exploit to search for using <str> pattern match"
    echo "  -w <str>    - exploit to search in web exploit site"
    echo "  -e <dir>    - exploit directory (default: /usr/share/exploits)"
    echo "  -b <url>    - give a new base url for packetstorm"
    echo "                (default: http://dl.packetstormsecurity.com/)"
    echo "  -l <file>   - give a new base path/file for website list option"
    echo "                (default: /usr/share/sploitctl/web/url.lst)"
    echo "  -c          - do not delete downloaded archive files"
    echo "  -n          - turn off colors"
    echo "  -v          - verbose mode (default: off)"
    echo "  -d          - debug mode (default: off)"
    echo ""
    echo "misc:"
    echo ""
    echo "  -V      - print version of packetstorm and exit"
    echo "  -H      - print this help and exit"

    exit ${SUCCESS}

    return ${SUCCESS}
}


# leet banner, very important
banner()
{
    yellow "--==[ sploitctl.sh by blackarch.org ]==--"

    return ${SUCCESS}
}


# check chosen website
check_site()
{
    if [ "${site}" = "?" ]
    then
        blue "[*] available exploit sites"
        green "  -> 0 - all exploit sites"
        green "  -> 1 - exploit-db.com"
        green "  -> 2 - packetstormsecurity.org"
        green "  -> 3 - m00-exploits (github)"
        exit ${SUCCESS}
    elif [ "${site}" != "0" -a "${site}" != "1" -a "${site}" != "2" \
      -a "${site}" != "3" ]
    then
        err "unknown exploit site"
    fi

    return ${SUCCESS}
}


# check argument count
check_argc()
{
    if [ ${#} -lt 1 ]
    then
        err "-H for help and usage"
    fi

    return ${SUCCESS}
}


# check if required arguments were selected
check_args()
{
    blue "[*] checking arguments" > ${VERBOSE} 2>&1

    if [ -z "${job}" ]
    then
        err "choose -f, -u or -s"
    fi

    if [ "${job}" = "search_web" ] && [ ! -f "${URL_FILE}" ]
    then
        err "failed to get url file for web searching - try -l <file>"
    fi
    return ${SUCCESS}
}


# parse command line options
get_opts()
{
    while getopts f:s:w:e:b:l:cnvdVH flags
    do
        case ${flags} in
            f)
                site="${OPTARG}"
                job="fetch"
                check_site
                ;;
            s)
                srch_str="${OPTARG}"
                job="search_db"
                ;;
            w)
                srch_str="${OPTARG}"
                job="search_web"
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
                CLEAN=0
                ;;
            n)
                COLORS=0
                ;;
            v)
                VERBOSE="/dev/stdout"
                ;;
            d)
                DEBUG="/dev/stdout"
                ;;
            V)
                echo "${VERSION}"
                exit ${SUCCESS}
                ;;
            H)
                usage
                ;;
            *)
                err "WTF?! mount /dev/brain"
                ;;
        esac
    done

    return ${SUCCESS}
}


# controller and program flow
main()
{
    check_argc "${@}"
    get_opts "${@}"
    banner
    check_args "${@}"

    if [ "${job}" = "fetch" ]
    then
        check_old_expl_dir
        make_exploit_dirs
        fetch
        extract
        clean
    elif [ "${job}" = "search_db" ]
    then
        search_db
    elif [ "${job}" = "search_web" ]
    then
        search_web
    else
        err "WTF?! mount /dev/brain"
    fi

    blue "[*] game over"

    return ${SUCCESS}
}


# program start
main "${@}"

# EOF
