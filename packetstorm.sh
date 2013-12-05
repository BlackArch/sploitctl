#!/bin/sh
################################################################################
#                                                                              #
# packetstorm.sh - fetch and update packetstorm exploit archives               #
#                                                                              #
# FILE                                                                         #
# packetstorm.sh                                                               #
#                                                                              #
# DATE                                                                         #
# 2013-12-04                                                                   #
#                                                                              #
# DESCRIPTION                                                                  #
# This script fetches yearly exploit archives of packetstormsecurity.org.      #
#                                                                              #
# AUTHORS                                                                      #
# noptrix@nullsecurity.net                                                     #
# archey@riseup.net                                                            #
################################################################################


# packetstorm.sh version
VERSION="packetstorm.sh v0.1"

# true / false
FALSE="0"
TRUE="1"

# return codes
SUCCESS="1337"
FAILURE="31337"

# verbose mode - default: quiet
VERBOSE="/dev/null"

# default directory for exploits
PSTORMDIR="/var/packetstorm"


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


# un-pack given (exploit) archive
unpack()
{
    return ${SUCCESS}
}


# update exploit directory / fetch new exploit archives
update()
{
    echo "[+] updating exploits"
    echo "+++ verbose mode on +++" > ${VERBOSE} 2>&1
    exit ${SUCCESS}

    return ${SUCCESS}
}


# fetch exploit archives
fetch()
{
    echo "[+] fetching exploit archives"
    echo "+++ verbose mode on +++" > ${VERBOSE} 2>&1
    exit ${SUCCESS}

    return ${SUCCESS}
}


# usage and help
usage()
{
    echo "usage:"
    echo ""
    echo "  packetstorm.sh -f | -u | [options] | <misc>"
    echo ""
    echo "options:"
    echo ""
    echo "  -f          - fetch and un-pack exploit archives"
    echo "  -u          - update exploit directory"
    echo "  -d <dir>    - define exploit directory (default: /var/packetstorm)"
    echo "  -v          - verbose mode (default: off)"
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
    echo "--==[ packetstorm.sh by noptrix & archey ]==--"

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
    return ${SUCCESS}
}


# parse command line options
get_opts()
{
    while getopts fud:vVH flags
    do
        case ${flags} in
            f)
                job="fetch"
                ;;
            u)
                job="update"
                ;;
            d)
                PSTORMDIR="${OPTARG}"
                ;;
            v)
                VERBOSE="/dev/stdout"
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

    red "red"
    blue "blue"
    yellow "yellow"
    green "green"

    if [ "${job}" = "fetch" ]
    then
        fetch
    elif [ "${job}" = "update" ]
    then
        update
    else
        err "WTF?! mount /dev/brain"
    fi

    return ${SUCCESS}
}


# program start
main ${*}

# EOF
