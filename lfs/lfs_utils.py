#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2021 Gabriele Iannetti <g.iannetti@gsi.de>
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


import os
import re
import traceback
import yaml
import socket
import logging
import subprocess

from enum import Enum
from datetime import datetime, timedelta


def check_value_for_type(value, type_):

    if value is not None and not isinstance(value, type_):

        # Better then nothing, but just the caller not the complete stack trace.
        caller = traceback.extract_stack(limit=2)[0]

        err = f"Value {value} must be type of {type_}\n" \
              f"Caller: Filename {caller.filename}, line {caller.lineno}, in {caller.name}"

        raise LfsUtilsError(err)

class LfsUtilsError(Exception):
    """Exception class LfsUtils specific errors."""

class LfsOstItem:

    def __init__(self, target, ost, state, active):

        self.target = target
        self.ost = ost
        self.state = state
        self.active = active
        self.ost_idx = ost

    @property
    def ost_idx(self):
        return self._ost_idx

    @ost_idx.setter
    def ost_idx(self, ost):

        if ost[0:3] != 'OST':
            raise LfsUtilsError(f"OST word not found in argument: {ost}")

        self._ost_idx = int(ost[3:], 16)

class StripeField(str, Enum):

    LMM_STRIPE_COUNT = 'lmm_stripe_count'
    LMM_STRIPE_OFFSET = 'lmm_stripe_offset'

class StripeInfo:

    def __init__(self, filename, count, index):

        self.filename = filename
        self.count = count
        self.index = index

class MigrateState(str, Enum):

    IGNORED = 'IGNORED'
    SKIPPED = 'SKIPPED'
    SUCCESS = 'SUCCESS'
    FAILED  = 'FAILED'

class MigrateResult:
    '''
    * IGNORED|{filename}
        - if file has stripe index not equal source index
        - if file has stripe index equal target index
    * SKIPPED|{filename}
        - if skip option enabled and file stripe count > 1
    * SUCCESS|{filename}|{ost_source_index}|{ost_target_index}|{time_elapsed}
        - if migration of file was successful
    * FAILED|{filename}|{return_code}|{error_message}
        - if migration of file failed
    '''

    def __init__(self, state, filename, time_elapsed, source_idx=None, target_idx=None, error_code=None, error_msg=None):

        check_value_for_type(state, MigrateState)
        check_value_for_type(filename, str)
        check_value_for_type(time_elapsed, timedelta)
        check_value_for_type(source_idx, int)
        check_value_for_type(target_idx, int)
        check_value_for_type(error_code, int)
        check_value_for_type(error_msg, str)

        if not filename:
            raise LfsUtilsError('No filename set.')

        if time_elapsed is None:
            raise LfsUtilsError('No time_elapsed set.')

        if state == MigrateState.FAILED:
            if not error_code:
                raise LfsUtilsError('State FAILED requires error_code to be set.')
            if not error_msg:
                raise LfsUtilsError('State FAILED requires error_msg to be set.')
        else:
            if error_code:
                raise LfsUtilsError(f"Not allowed to set error_code in state {state}.")
            if error_msg:
                raise LfsUtilsError(f"Not allowed to set error_msg in state {state}.")

        self.state = state
        self.filename = filename
        self.source_idx = source_idx
        self.target_idx = target_idx
        self.time_elapsed = time_elapsed
        self.error_code = error_code
        self.error_msg = error_msg

    def __str__(self) -> str:
        return f"{self.state}|{self.filename}|{self.time_elapsed}|{self.source_idx}|{self.target_idx}|{self.error_code}|{self.error_msg}"

class LfsUtils:

    _REGEX_STR_OST_STATE = r"\-(OST[a-z0-9]+)\-[a-z0-9-]+\s(.+)"
    _REGEX_STR_OST_FILL_LEVEL = r"(\d{1,3})%.*\[OST:([0-9]{1,4})\]"
    _REGEX_STR_OST_CONN_UUID = r"ost_conn_uuid=([\d\.]+)@"

    _REGEX_PATTERN_OST_FILL_LEVEL = re.compile(_REGEX_STR_OST_FILL_LEVEL)
    _REGEX_PATTERN_OST_CONN_UUID = re.compile(_REGEX_STR_OST_CONN_UUID)

    _MAX_OST_INDEX = 65535

    def __init__(self, lfs, lctl):

        if not os.path.isfile(lfs):
            raise LfsUtilsError(f"LFS binary was not found under: '{lfs}'")

        if not os.path.isfile(lctl):
            raise LfsUtilsError(f"LCTL binary was not found under: '{lctl}'")

        self.lfs = lfs
        self.lctl = lctl

    # TODO: Return dict for multiple targets with proper OST items.
    def create_ost_item_list(self, target):

        try:
            args = ['sudo', self.lfs, 'check', 'osts']
            result = subprocess.run(args, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise LfsUtilsError(err.stderr.decode('UTF-8'))

        ost_list = []

        regex_str = target + LfsUtils._REGEX_STR_OST_STATE
        logging.debug("Using regex for `lfs check osts`: %s", regex_str)
        pattern = re.compile(regex_str)

        for line in result.stdout.decode('UTF-8').strip().split('\n'):

            match = pattern.match(line.strip())

            if match:

                ost = match.group(1)
                state = match.group(2)

                if state == 'active.':
                    ost_list.append(LfsOstItem(target, ost, state, True))
                else:
                    ost_list.append(LfsOstItem(target, ost, state, False))

            else:
                logging.warning("No regex match for line: %s", line)

        return ost_list

    def is_ost_idx_active(self, target, ost_idx):

        for ost_item in self.create_ost_item_list(target):

            if ost_item.ost_idx == ost_idx:
                return ost_item.active

        raise LfsUtilsError(f"Index not found: {ost_idx}")

    def set_stripe(self, ost_idx, file_path):

        if ost_idx is None:
            raise LfsUtilsError('Argument ost_idx is not set.')

        if file_path is None or not file_path:
            raise LfsUtilsError('Argument file_path is not set.')

        if not isinstance(ost_idx, int):
            raise LfsUtilsError('Argument ost_idx must be type int.')

        if not isinstance(file_path, str):
            raise LfsUtilsError('Argument file_path must be type str.')

        logging.debug("Setting stripe for file: %s - OST: %i", file_path, ost_idx)

        try:
            args = [self.lfs, 'setstripe', '-i', str(ost_idx), file_path]
            subprocess.run(args, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise LfsUtilsError(err.stderr.decode('UTF-8'))

    def stripe_info(self, filename) -> StripeInfo:
        """
        Raises
        ------
        LfsUtilsError
            * If a field is not found in retrieved stripe info for given file.
            * If execution of 'lfs getstripe' returns an error.

        Returns
        -------
        A StripeInfo object.
        """

        try:

            args = [self.lfs, 'getstripe', '-c', '-i', '-y', filename]

            result = subprocess.run(args, check=True, capture_output=True)

            # TODO: Write a test that checks on dict type and content...
            fields = yaml.safe_load(result.stdout)

            lmm_stripe_count = 0
            if StripeField.LMM_STRIPE_COUNT in fields:
                lmm_stripe_count = fields[StripeField.LMM_STRIPE_COUNT]
            else:
                raise LfsUtilsError(f"Field {StripeField.LMM_STRIPE_COUNT} not found in stripe info: {result.stdout}")

            lmm_stripe_offset = 0
            if StripeField.LMM_STRIPE_OFFSET in fields:
                lmm_stripe_offset = fields[StripeField.LMM_STRIPE_OFFSET]
            else:
                raise LfsUtilsError(f"Field {StripeField.LMM_STRIPE_OFFSET} not found in stripe info: {result.stdout}")

            return StripeInfo(filename, lmm_stripe_count, lmm_stripe_offset)

        except subprocess.CalledProcessError as err:
            raise LfsUtilsError(err.stderr.decode('UTF-8'))

    def migrate_file(self, filename, source_idx=None, target_idx=None, block=False, skip=True) -> str:

        migrate_result = ''

        if not filename:
            raise LfsUtilsError('Empty filename provided.')

        check_value_for_type(filename, str)

        if source_idx is not None:
            check_value_for_type(source_idx, int)

        if target_idx is not None:
            check_value_for_type(target_idx, int)

        if block:
            check_value_for_type(block, bool)

        if skip:
            check_value_for_type(skip, bool)

        stripe_info = self.stripe_info(filename)

        if skip and stripe_info.count > 1:
            migrate_result = MigrateResult(MigrateState.SKIPPED, filename, timedelta(0), source_idx, target_idx)
        elif source_idx is not None and stripe_info.index != source_idx:
            migrate_result = MigrateResult(MigrateState.IGNORED, filename, timedelta(0), source_idx, target_idx)
        elif target_idx is not None and stripe_info.index == target_idx:
            migrate_result = MigrateResult(MigrateState.IGNORED, filename, timedelta(0), source_idx, target_idx)
        else:

            try:
                args = [self.lfs, 'migrate']

                if block:
                    args.append('--block')
                else:
                    args.append('--non-block')

                if target_idx > -1:
                    args.append('-i')
                    args.append(str(target_idx))

                if stripe_info.count > 0:
                    args.append('-c')
                    args.append(str(stripe_info.count))

                args.append(filename)

                start_time = datetime.now()
                subprocess.run(args, check=True, capture_output=True)
                time_elapsed = datetime.now() - start_time

                migrate_result = MigrateResult(MigrateState.SUCCESS, filename, time_elapsed, source_idx, target_idx)

            except subprocess.CalledProcessError as err:

                stderr = ''

                if err.stderr:
                    stderr = err.stderr.decode('UTF-8')

                migrate_result = MigrateResult(MigrateState.FAILED, filename, time_elapsed, source_idx, target_idx, err.returncode, stderr)

        return migrate_result

    def retrieve_ost_fill_level(self, fs_path) -> dict:

        ost_fill_level_dict = {}

        if not fs_path:
            raise LfsUtilsError('Lustre file system path is not set!')

        try:

            args = ['sudo', self.lfs, 'df', fs_path]

            result = subprocess.run(args, check=True, capture_output=True)

            for line in result.stdout.decode('UTF-8').strip().split('\n'):

                match = LfsUtils._REGEX_PATTERN_OST_FILL_LEVEL.search(line.strip())

                if match:

                    fill_level = int(match.group(1))
                    ost_idx = match.group(2)

                    ost_fill_level_dict[ost_idx] = fill_level

            if not ost_fill_level_dict:
                raise LfsUtilsError('Lustre OST fill levels are empty!')

        except subprocess.CalledProcessError as err:
            raise LfsUtilsError(err.stderr.decode('UTF-8'))

        return ost_fill_level_dict

    def lookup_ost_to_oss(self, fs_name, ost, caching=True) -> str:

        hostname = ''

        if not fs_name:
            raise LfsUtilsError('Lustre file system name must be set.')

        if ost is None:
            raise LfsUtilsError('OST index must be set.')

        check_value_for_type(fs_name, str)
        check_value_for_type(ost, int)

        if ost < 0 or ost > LfsUtils._MAX_OST_INDEX:
            raise LfsUtilsError(f"OST index {ost} invalid. Must be in range between 0 and {LfsUtils._MAX_OST_INDEX}.")

        # TODO: Lookup in cache

        ost_hex = hex(ost).split('x')[-1].zfill(4)

        param_value = f"osc.{fs_name}-OST{ost_hex}*.ost_conn_uuid"

        args = [self.lctl, 'get_param', param_value]

        result = subprocess.run(args, check=True, capture_output=True)

        match = LfsUtils._REGEX_PATTERN_OST_CONN_UUID.search(result.stdout.decode('UTF-8'))

        if not match:
            raise LfsUtilsError(f"No match for ost_conn_uuid for OST {ost} on file system {fs_name}")

        ip_addr = match.group(1)

        host_info = socket.gethostbyaddr(ip_addr)

        if not host_info:
            raise LfsUtilsError(f"No host information retrieved from socket.gethostbyaddr() for IP addr {ip_addr}")

        check_value_for_type(host_info, tuple)

        if len(host_info) != 3:
            raise LfsUtilsError(f"Broken interface for value {host_info} on socket.gethostbyaddr()")

        hostname = host_info[0]

        if not hostname:
            raise LfsUtilsError(f"No hostname found for OST {ost} on file system {fs_name}")

        check_value_for_type(hostname, str)

        return hostname

    def retrieve_ost_to_oss_map(self, fs_name, caching=True) -> dict:
        pass

    def is_ost_writable(self, ost, file_path) -> bool:

        if file_path is None:
            raise LfsUtilsError('File path must be set.')

        if ost is None:
            raise LfsUtilsError('OST index must be set.')

        check_value_for_type(ost, int)
        check_value_for_type(file_path, str)

        if ost < 0 or ost > LfsUtils._MAX_OST_INDEX:
            raise LfsUtilsError(f"OST index {ost} invalid. Must be in range between 0 and {LfsUtils._MAX_OST_INDEX}.")

        if os.path.exists(file_path):
            raise LfsUtilsError(f"File already exists: {file_path}")

        try:

            self.set_stripe(ost, file_path)

            stripe_info = self.stripe_info(file_path)

            if stripe_info.index == ost:

                if os.path.exists(file_path):
                    os.remove(file_path)

                return True

        except Exception as err:
            logging.error(err)

        return False
