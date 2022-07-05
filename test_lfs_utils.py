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

import unittest

from datetime import timedelta
from lfs.lfs_utils import LfsUtils, LfsUtilsError, MigrateResult, MigrateState


class TestLfsUtils(unittest.TestCase):

    @classmethod
    def create_migrate_result_with_no_filename(cls, state):
        MigrateResult(state, '', timedelta(0))

    @classmethod
    def create_migrate_result_with_no_time_elapsed(cls, state):
        MigrateResult(state, 'test.tmp', None)

    @classmethod
    def create_migrate_result_with_just_error_code(cls, state):
        MigrateResult(state, 'test.tmp', timedelta(0), error_code=12)

    @classmethod
    def create_migrate_result_with_just_error_msg(cls, state):
        MigrateResult(state, 'test.tmp', timedelta(0), error_msg='An error occured.')

    def test_migrate_result_ignored(self):

        result = MigrateResult(MigrateState.IGNORED, 'test.tmp', timedelta(minutes=1, seconds=13))
        self.assertEqual(result.__str__(), 'IGNORED|test.tmp|0:01:13|None|None|None|None')

        result = MigrateResult(MigrateState.IGNORED, 'test.tmp', timedelta(minutes=1, seconds=13), 4, 67)
        self.assertEqual(result.__str__(), 'IGNORED|test.tmp|0:01:13|4|67|None|None')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_filename(MigrateState.IGNORED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_time_elapsed(MigrateState.IGNORED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_code(MigrateState.IGNORED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_msg(MigrateState.IGNORED)

    def test_migrate_result_skipped(self):

        result = MigrateResult(MigrateState.SKIPPED, 'test.tmp', timedelta(minutes=1, seconds=13))
        self.assertEqual(result.__str__(), 'SKIPPED|test.tmp|0:01:13|None|None|None|None')

        result = MigrateResult(MigrateState.SKIPPED, 'test.tmp', timedelta(minutes=1, seconds=13), 4, 67)
        self.assertEqual(result.__str__(), 'SKIPPED|test.tmp|0:01:13|4|67|None|None')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_filename(MigrateState.SKIPPED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_time_elapsed(MigrateState.SKIPPED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_code(MigrateState.SKIPPED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_msg(MigrateState.SKIPPED)

    def test_migrate_result_success(self):

        result = MigrateResult(MigrateState.SUCCESS, 'test.tmp', timedelta(minutes=1, seconds=13))
        self.assertEqual(result.__str__(), 'SUCCESS|test.tmp|0:01:13|None|None|None|None')

        result = MigrateResult(MigrateState.SUCCESS, 'test.tmp', timedelta(minutes=1, seconds=13), 4, 67)
        self.assertEqual(result.__str__(), 'SUCCESS|test.tmp|0:01:13|4|67|None|None')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_filename(MigrateState.SUCCESS)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_time_elapsed(MigrateState.SUCCESS)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_code(MigrateState.SUCCESS)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_msg(MigrateState.SUCCESS)

    def test_migrate_result_failed(self):

        result = MigrateResult(MigrateState.FAILED, 'test.tmp', timedelta(minutes=1, seconds=13), 4, 67, 12, 'An error occured.')
        self.assertEqual(result.__str__(), 'FAILED|test.tmp|0:01:13|4|67|12|An error occured.')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_filename(MigrateState.FAILED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_no_time_elapsed(MigrateState.FAILED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_code(MigrateState.FAILED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtils.create_migrate_result_with_just_error_msg(MigrateState.FAILED)

    def test_lookup_ost_to_oss(self):

        with self.assertRaises(LfsUtilsError):
            LfsUtils.lookup_ost_to_oss(self=None, fs_name=None, ost=None)

        with self.assertRaises(LfsUtilsError):
            LfsUtils.lookup_ost_to_oss(self=None, fs_name='lustre-fs', ost=None)

        with self.assertRaises(LfsUtilsError):
            LfsUtils.lookup_ost_to_oss(self=None, fs_name='lustre-fs', ost='783')

        with self.assertRaises(LfsUtilsError):
            LfsUtils.lookup_ost_to_oss(self=None, fs_name='lustre-fs', ost=65566)

