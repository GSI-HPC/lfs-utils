#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Gabriele Iannetti <g.iannetti@gsi.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import argparse
import logging

from minimal_python import MinimalPython
from lfs_utils import LfsUtils, LfsUtilsError


def init_arg_parser():

    parser = argparse.ArgumentParser(description='Example main programm for executing LfsUtils.')

    parser.add_argument('-n',
                        '--fs-name',
                        dest='fs_name',
                        required=True,
                        type=str,
                        help='Specify file system name.')

    parser.add_argument('-p',
                        '--fs-path',
                        dest='fs_path',
                        required=False,
                        type=str,
                        default='/lustre',
                        help='Specify file system path.')

    parser.add_argument('-t',
                        '--test-file',
                        dest='test_file',
                        required=True,
                        type=str,
                        help='Specify test file.')

    parser.add_argument('-o',
                        '--ost-index',
                        dest='ost_index',
                        required=False,
                        type=int,
                        default=3,
                        help='Specify ost index.')

    parser.add_argument('-l',
                        '--log-file',
                        dest='log_file',
                        required=False,
                        type=str,
                        help='Specify log file.')

    parser.add_argument('-D',
                        '--debug',
                        dest='enable_debug',
                        required=False,
                        action='store_true',
                        help='Enable debug.')

    parser.add_argument('-v',
                        '--version',
                        dest='print_version',
                        required=False,
                        action='store_true',
                        help='Print library version number.')

    return parser.parse_args()


def init_logging(log_file, enable_debug):

    if enable_debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    if log_file:
        logging.basicConfig(filename=log_file, level=log_level, format="%(asctime)s - %(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s: %(message)s")


def main():

    try:

        MinimalPython.check()

        args = init_arg_parser()

        lfs_utils = LfsUtils()

        init_logging(args.log_file, args.enable_debug)

        fs_name                = args.fs_name
        fs_path                = args.fs_path
        test_file              = args.test_file
        ost_index              = args.ost_index

        logging.info('Started')

        comp_states = lfs_utils.retrieve_component_states()
        fs_states = comp_states[fs_name]

        logging.info(f"Count of MDTs: {len(fs_states.mdts)} - For file system: {fs_name}")
        logging.info(f"Count of OSTs: {len(fs_states.osts)} - For file system: {fs_name}")

        logging.info(f"OST {ost_index} is active: {lfs_utils.is_ost_idx_active(fs_name, ost_index)} - On file system: {fs_name}")

        logging.info(f"OST {ost_index} is writable: {lfs_utils.is_ost_writable(ost_index, test_file)}")

        lfs_utils.set_ost_file_stripe(test_file, ost_index)

        stripe_info = lfs_utils.stripe_info(test_file)
        logging.info(f"Stripe info for file: {stripe_info.filename} - OST index: {stripe_info.index} - Stripe count: {stripe_info.count}")

        logging.info(lfs_utils.migrate_file(test_file, ost_index, 0))

        logging.info(lfs_utils.migrate_file(test_file))

        logging.info(f"Size of OST fill level items: {len(lfs_utils.retrieve_ost_fill_level(fs_path))}")

        logging.info(f"Hostname for OST {ost_index} on file system {fs_name}: {lfs_utils.lookup_ost_to_oss(fs_name, ost_index)}")

        logging.info('Finished')

    except Exception:
        logging.exception('Caught exception in main function')


if __name__ == '__main__':
    main()
