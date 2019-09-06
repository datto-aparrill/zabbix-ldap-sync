#!/usr/bin/env python3
#
# Copyright (c) 2017-now Marc Schöchlin <ms@256bit.org>
# Copyright (c) 2013-2014 Marin Atanasov Nikolov <dnaeon@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
#    in this position and unchanged.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
The zabbix-ldap-sync script is used for syncing LDAP users with Zabbix.

"""
import warnings
import traceback
import sys
import os
import logging
from docopt import docopt

from .zabbixldapconf import ZabbixLDAPConf
from .zabbixconn import ZabbixConn
from .ldapconn import LDAPConn


def main():
    usage = """
Usage: zabbix-ldap-sync [-lsrwdn] [--verbose] [--dryrun] -f <config>
       zabbix-ldap-sync -v
       zabbix-ldap-sync -h

Options:
  -h, --help                    Display this usage info
  -v, --version                 Display version and exit
  -l, --lowercase               Create AD user names as lowercase
  -s, --skip-disabled           Skip disabled AD users
  -r, --recursive               Resolves AD group members recursively (i.e. nested groups)
  -w, --wildcard-search         Search AD group with wildcard (e.g. R.*.Zabbix.*) - TESTED ONLY with Active Directory
  -d, --delete-orphans          Delete Zabbix users that don't exist in a LDAP group
  -n, --no-check-certificate    Don't check Zabbix server certificate
  --verbose                     Print debug message from ZabbixAPI
  --dryrun                      Just simulate zabbix interaction
  -f <config>, --file <config>  Configuration file to use

"""
    args = docopt(usage, version="0.1.1")

    config = ZabbixLDAPConf(args['--file'])

    config.zbx_lowercase = args['--lowercase']
    config.zbx_skipdisabled = args['--skip-disabled']
    config.zbx_deleteorphans = args['--delete-orphans']
    config.zbx_nocheckcertificate = args['--no-check-certificate']

    config.ldap_recursive = args['--recursive']
    config.ldap_wildcard_search = args['--wildcard-search']

    config.verbose = args['--verbose']
    config.dryrun = args['--dryrun']

    level = logging.DEBUG if config.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    ldap_conn = LDAPConn(config)

    zabbix_conn = ZabbixConn(config, ldap_conn)

    zabbix_conn.connect()

    zabbix_conn.create_missing_groups()

    zabbix_conn.sync_users()

if __name__ == '__main__':
    main()
