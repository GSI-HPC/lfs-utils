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
import datetime
import logging
import sys
import os

from lfs.lfs_utils import LFSUtils, LFSUtilsError, MigrateResult, MigrateState


def init_arg_parser():

    parser = argparse.ArgumentParser(description='Example main programm for executing LFSUtils.')

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

        args = init_arg_parser()

        migrate_result = MigrateResult(MigrateState.SUCCESS, 'tmp/whatever.tmp', datetime.timedelta(0))
        logging.info(migrate_result)

        lfs_utils = LFSUtils('/usr/bin/lfs')

        if args.print_version:
            print(f"{lfs_utils.version()}")
            sys.exit()

        init_logging(args.log_file, args.enable_debug)

        logging.info("Started")

        try:
            logging.info(f"Size of OSTItem list: {len(lfs_utils.create_ost_item_list('hebe'))}")
        except LFSUtilsError as err:
            logging.error(err)

        try:
            logging.info(f"OST 0 is active: {lfs_utils.is_ost_idx_active('hebe', '0')}")
        except LFSUtilsError as err:
            logging.error(err)

        test_file = '/lustre/hebe/hpc/iannetti/test_set_stripe.tmp'

        try:
            lfs_utils.set_stripe('0', test_file)
        except LFSUtilsError as err:
            logging.error(err)

        try:
            logging.info(lfs_utils.stripe_info(test_file))
        except LFSUtilsError as err:
            logging.error(err)

        try:
            logging.info(lfs_utils.migrate_file(test_file, 0, 1))
        except LFSUtilsError as err:
            logging.error(err)

        try:
            logging.info(f"Size of OST fill level items: {len(lfs_utils.retrieve_ost_fill_level('/lustre'))}")
        except LFSUtilsError as err:
            logging.error(err)

        logging.info("Finished")

    except Exception as err:

        _, _, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error(f"Exception in {filename} (line: {exc_tb.tb_lineno}): {err}")


if __name__ == '__main__':
    main()