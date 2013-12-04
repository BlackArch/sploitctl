#!/bin/sh
################################################################################
#                                                                              #
# packetstorm.sh - get and update packetstorm exploit archives                 #
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
# AUTHOR                                                                       #
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


# a routine which does foobar
dummy()
{
    echo "test for command line option '-d': ${dummy}"
    echo "+++ verbose mode on +++" > ${VERBOSE} 2>&1
    exit ${SUCCESS}

    return ${SUCCESS}
}


# usage and help
usage()
{
    echo "usage:"
    echo ""
    echo "  packetstorm.sh -d <dummy> [options] | <misc>"
    echo ""
    echo "options:"
    echo ""
    echo "  -d <dummy>  - dummy for foobar"
    echo "  -v          - verbose mode (default: off)"
    echo ""
    echo "misc:"
    echo ""
    echo "  -V          - print version of packetstorm and exit"
    echo "  -H          - print this help and exit"

    exit ${SUCCESS}
    
    return ${SUCCESS}
}


# leet banner, very important
banner()
{
    echo "--==[ packetstorm.sh by noptrix and archey ]==--"

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
    while getopts d:vVH flags
    do
        case ${flags} in
            d)
                dummy="${OPTARG}"
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
    dummy

    return ${SUCCESS}
}


# program start
main ${*}

# EOF
