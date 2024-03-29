#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# © Copyright 2023 GSI Helmholtzzentrum für Schwerionenforschung
#
# This software is distributed under
# the terms of the GNU General Public Licence version 3 (GPL Version 3),
# copied verbatim in the file "LICENCE".

import argparse
import logging

from ClusterShell.NodeSet import NodeSet
from ClusterShell.RangeSet import RangeSet

from lfsutils.lib import LfsUtils

import lfsutils.lib

def init_arg_parser():

    parser = argparse.ArgumentParser(description='LFSUtils CLI Tool')
    parser.add_argument('-D', '--debug', dest='debug', required=False, action='store_true', help='Enable debug')

    subparsers = parser.add_subparsers(dest='sub_command', help='sub-command help')

    parser_oss = subparsers.add_parser(name='oss', description='Lookup OSS by specifying an OST RangeSet', help='OSS lookup by OST RangeSet')
    parser_oss.add_argument('-D', '--debug', dest='debug', required=False, action='store_true', help='Enable debug')
    parser_oss.add_argument('fsname', type=str, help='Filesystem name')
    parser_oss.add_argument('rangeset', type=str, help='RangeSet with OST decimal indexes e.g. "30-50,100-120". For hexadecimal see -x/--hex option.')
    parser_oss.add_argument('-x', '--hex', dest='hex', required=False, default=False, action='store_true', help='Enable hexadecimal rangeset specification for OSTs e.g. \"0000, 00D6-00F1, 00FF-01A0\"')

    parser_ost = subparsers.add_parser(name='ost', description='Lookup OST by specifying an OSS NodeSet', help='OST lookup by OSS NodeSet')
    parser_ost.add_argument('-D', '--debug', dest='debug', required=False, action='store_true', help='Enable debug')
    parser_ost.add_argument('fsname', type=str, help='Filesystem name')
    parser_ost.add_argument('nodeset', type=str, help='FQDN specified OSS as NodeSet e.g. \"oss[0-9,12-20].domain\"')

    return parser.parse_args()

def init_logging(debug):

    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s: %(message)s")

def main():

    try:

        args = init_arg_parser()

        lfs_utils = LfsUtils()

        init_logging(args.debug)

        logging.debug('Started')

        if args.sub_command == 'oss':

            if args.hex:
                rangeset: RangeSet = lfsutils.lib.create_rangeset_from_hex(args.rangeset)
            else:
                rangeset: RangeSet = RangeSet(args.rangeset)

            logging.debug("Lookup OSS by OST RangeSet %s", rangeset)

            for oss, ost_list in lfs_utils.lookup_oss_by_ost_rangeset(args.fsname, rangeset).items():
                print(f"{oss} - {ost_list}")

        elif args.sub_command == 'ost':

            nodeset: NodeSet = NodeSet(args.nodeset)

            logging.debug("Lookup OST by OSS NodeSet %s", nodeset)

            for oss, ost_list in lfs_utils.lookup_ost_by_oss_nodeset(args.fsname, nodeset).items():
                print(f"{oss} - {ost_list}")

        else:
            pass

        logging.debug('Finished')

    except Exception:
        logging.exception('Caught exception in main function')

if __name__ == '__main__':
    main()
