#!/bin/sh
################################################################################
#                                                                              #
# sploitctl.sh - fetch, update, search exploits archives from exploit sites    #
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
################################################################################


# sploitctl.sh version
VERSION="sploitctl.sh v0.1"

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
EXPLOIT_DIR="/var/exploits"

# link to exploit-db's exploit archive
XPLOITDB_URL="http://www.exploit-db.com/archive.tar.bz2"

# base url for packetstorm
PSTORM_URL="http://packetstorm.wowhacker.com/"

# clean up, delete downloaded archive files (default: off)
CLEAN=1

# user agent string for curl
USERAGENT="blackarch/${VERSION}" 


# print line in blue
blue()
{
    msg="${*}"

    echo "`tput setaf 4`${msg}`tput sgr0`"

    return ${SUCCESS}
}


# print line in yellow
yellow()
{
    msg="${*}"

    echo "`tput setaf 3`${msg}`tput sgr0`"

    return ${SUCCESS}
}


# print line in green
green()
{
    msg="${*}"

    echo "`tput setaf 2`${msg}`tput sgr0`"

    return ${SUCCESS}
}


# print line in red
red()
{
    msg="${*}"

    echo "`tput setaf 1`${msg}`tput sgr0`"

    return ${SUCCESS}
}


# print warning
warn()
{
    echo "[!] WARNING: ${*}"

    return ${SUCCESS}
}


# print error and exit
err()
{
    echo "[-] ERROR: ${*}"
    exit ${FAILURE}

    return ${SUCCESS}
}


# delete downloaded archive files
clean()
{
    if [ ${CLEAN} -eq 1 ]
    then
        echo "[+] deleting archive files" > ${VERBOSE} 2>&1
        rm -rf ${EXPLOIT_DIR}/{*.tar,*.tgz,*.tar.bz2} > ${DEBUG} 2>&1
    fi

    return ${SUCCESS}
}


# search exploit(s) for given search pattern
search()
{
    echo "[+] searching exploit"

    grep -ri "${srch_str}" ${xploitdb_dir} > ${DEBUG} 2>&1

    return ${SUCCESS}
}


# exploit packetstorm archives and do changes if necessary
extract_pstorm()
{
    for f in *.tgz
    do
        tar xfvz ${f} -C "${pstorm_dir}/" > ${DEBUG} 2>&1
    done
 
    return ${SUCCESS}
}


# exploit exploit-db archive and do changes if necessary
extract_xploitdb()
{
    # use bunzip because of -j vs. -y flag on $OS
    bunzip2 archive.tar.bz2 > ${DEBUG} 2>&1
    tar xfv archive.tar > ${DEBUG} 2>&1
    
    mv platforms/* ${xploitdb_dir} > ${DEBUG} 2>&1
    mv files.csv ${xploitdb_dir} > ${DEBUG} 2>&1
    
    rm -rf platforms > ${DEBUG} 2>&1
    
    find ${xploitdb_dir} -type f -exec chmod 640 {} \; > ${DEBUG} 2>&1
 
    return ${SUCCESS}
}


# extract exploit archives
extract()
{
    echo "[+] extracting exploit archives"

    make_exploit_dirs
    
    case ${site} in
        0)
            extract_xploitdb
            extract_pstorm
            ;;
        1)
            echo "  -> extracting exploit-db archives ..." > ${VERBOSE} 2>&1
            extract_xploitdb
            ;;
        2)
            echo "  -> extracting packetstorm archives ..." > ${VERBOSE} 2>&1
            extract_pstorm
            ;;
    esac

    return ${SUCCESS}
}


# update exploit directory / fetch new exploit archives
update()
{
    echo "[+] updating exploit collection"
    
    # there is currently no need for doing checks and updates
    echo "  -> updating exploit-db ..." > ${VERBOSE} 2>&1
    fetch_xploitdb
    extract_xploitdb

    echo "  -> updating packetstorm ..." > ${VERBOSE} 2>&1

    return ${SUCCESS}
}


# download exploit archives from packetstorm
fetch_pstorm()
{
    # enough for the next 90 years ;)
    cur_year=`date +%Y | sed 's/.*20//'`
    y=0

    echo "  -> downloading archives from packetstorm ..." > ${VERBOSE} 2>&1

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
            echo "  -> downloading ${year}${month}-exploits.tgz ..." \
                > ${VERBOSE} 2>&1
            curl -A ${USERAGENT} "blackarch/sploitctl ${VERSION}" -C - -O \
                "${PSTORM_URL}/${year}${month}-exploits/${year}${month}-exploits.tgz" \
                > ${DEBUG} 2>&1
        done
        y=`expr ${y} + 1`
    done

    return ${SUCCESS}
}


# download exploit archives from exploit-db
fetch_xploitdb()
{
    echo "  -> downloading archive from exploit-db ..." > ${VERBOSE} 2>&1

    curl -A ${USERAGENT} -C - -O ${XPLOITDB_URL} > ${DEBUG} 2>&1

    return ${SUCCESS}
}


# download exploit archives from chosen sites
fetch()
{
    echo "[+] downloading exploit archives"

    if [ "${site}" = "0" -o "${site}" = "1" ]
    then
        fetch_xploitdb
    fi
    if [ "${site}" = "0" -o "${site}" = "2" ]
    then
        fetch_pstorm
    fi

    return ${SUCCESS}
}


# define exploit dirs for each site
make_exploit_dirs()
{
    xploitdb_dir="${EXPLOIT_DIR}/exploit-db"
    pstorm_dir="${EXPLOIT_DIR}/packetstorm"

    if [ ! -d ${xploitdb_dir} ]
    then
        mkdir ${xploitdb_dir} > ${DEBUG} 2>&1
    fi

    if [ ! -d ${pstorm_dir} ]
    then
        mkdir ${pstorm_dir} > ${DEBUG} 2>&1
    fi

    return ${SUCCESS}
}


# usage and help
usage()
{
    echo "usage:"
    echo ""
    echo "  sploitctl.sh -f <arg> | -u <arg> | -s <arg> [options] | <misc>"
    echo ""
    echo "options:"
    echo ""
    echo "  -f <num>    - download and extract exploit archives from chosen"
    echo "                websites - ? to list sites"
    echo "  -u <num>    - update exploit directories from chosen"
    echo "                websites - ? to list sites"
    echo "  -s <str>    - exploit to search for using <str> pattern match"
    echo "  -e <dir>    - exploit directory (default: /var/exploits)"
    echo "  -b <url>    - give a new base url for packetstorm"
    echo "                (default: http://packetstorm.wowhacker.com/)"
    echo "  -c          - do not delete downloaded archive files"
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
    echo "--==[ sploitctl.sh by noptrix & archey ]==--"

    return ${SUCCESS}
}


# check chosen website
check_site()
{
    if [ "${site}" = "?" ]
    then
        echo "[+] available exploit sites"
        echo "  -> 0 - all exploit sites"
        echo "  -> 1 - exploit-db.com"
        echo "  -> 2 - packetstormsecurity.org"
        exit ${SUCCESS}
    elif [ "${site}" != "0" -a "${site}" != "1" -a "${site}" != "2" ]
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
    echo "[+] checking arguments" > ${VERBOSE} 2>&1

    if [ -z "${job}" ]
    then
        err "choose -f, -u or -s"
    fi

    return ${SUCCESS}
}


# parse command line options
get_opts()
{
    while getopts f:u:s:e:b:cvdVH flags
    do
        case ${flags} in
            f)
                site="${OPTARG}"
                job="fetch"
                check_site
                ;;
            u)
                site="${OPTARG}"
                job="update"
                check_site
                ;;
            s)
                srchstr="${OPTARG}"
                job="search"
                ;;
            e)
                EXPLOIT_DIR="${OPTARG}"
                ;;
            b)
                PSTORM_URL="${OPTARG}"
                ;;
            c)
                CLEAN=0
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
    banner
    check_argc ${*}
    get_opts ${*}
    check_args ${*}

    if [ ! -d ${EXPLOIT_DIR} ]
    then
      mkdir ${EXPLOIT_DIR} > ${DEBUG} 2>&1
    fi

    cd "${EXPLOIT_DIR}"

    if [ "${job}" = "fetch" ]
    then
        #fetch
        extract
        clean
    elif [ "${job}" = "update" ]
    then
        update
        clean
    elif [ "${job}" = "search" ]
    then
        search
    else
        err "WTF?! mount /dev/brain"
    fi

    return ${SUCCESS}
}


# program start
main ${*}

# EOF
