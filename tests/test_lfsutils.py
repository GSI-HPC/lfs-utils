#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# © Copyright 2023 GSI Helmholtzzentrum für Schwerionenforschung
#
# This software is distributed under
# the terms of the GNU General Public Licence version 3 (GPL Version 3),
# copied verbatim in the file "LICENCE".

from datetime import timedelta

import unittest

def load_lfsutils_module_from_local_path():

    from pathlib import PurePosixPath
    import sys, os

    sys.path.append(f"{PurePosixPath(os.path.dirname(os.path.realpath(__file__))).parents[0].as_posix()}/src/")

load_lfsutils_module_from_local_path()

from lfsutils.lib import LfsUtils, LfsUtilsError, MigrateResult, MigrateState
import lfsutils.lib as lfsutils

class TestLfsUtils(unittest.TestCase):

    def test_retrieve_ost_fill_level(self):

        ost_fill_level = LfsUtils.retrieve_ost_disk_usage(self=None, fs_path='/lustre', file='lfs_df.txt')

        self.assertEqual(len(ost_fill_level), 784)

    def test_retrieve_component_states(self):

        comp_states = LfsUtils.retrieve_component_states(self=None, file='lfs_check_servers.txt')

        self.assertEqual(len(comp_states['lustre'].mdts), 3)
        self.assertEqual(len(comp_states['lustre'].osts), 784)

        self.assertEqual(len(comp_states['lustrefs2'].mdts), 3)
        self.assertEqual(len(comp_states['lustrefs2'].osts), 10)

        self.assertEqual(comp_states['lustre'].osts[0].active, True)
        self.assertEqual(comp_states['lustrefs2'].osts[3].active, False)

    def test_stripe_info(self):

        stripe_info = LfsUtils.stripe_info(self=None, filename=None, file='lfs_getstripe.txt')

        self.assertEqual(1, stripe_info.count)
        self.assertEqual(542, stripe_info.index)

    def test_conv_obj(self):

        self.assertEqual(lfsutils.conv_obj(None), '')
        self.assertEqual(lfsutils.conv_obj(45), '45')
        self.assertEqual(lfsutils.conv_obj('SUCCESS'), 'SUCCESS')

        with self.assertRaises(TypeError):
            lfsutils.conv_obj(12.7)

    def test_to_ost_hex(self):

        self.assertEqual(lfsutils.to_ost_hex(12), '000c')

        with self.assertRaises(TypeError):
            lfsutils.to_ost_hex('45')

        with self.assertRaises(TypeError):
            lfsutils.to_ost_hex(67.32)

    def test_create_rangeset_from_hex(self):
        self.assertEqual(
            str(lfsutils.create_rangeset_from_hex('0000, 00FF, ff00-FF10, dd23')),
            '0,255,56611,65280-65296')

class TestLfsUtilsMigration(unittest.TestCase):

    @classmethod
    def create_migrate_result_with_no_filename(cls, state):
        MigrateResult(state, '', timedelta(0))

    @classmethod
    def create_migrate_result_with_no_time_elapsed(cls, state):
        MigrateResult(state, 'test.tmp', None)

    @classmethod
    def create_migrate_result_with_just_error_code(cls, state):
        MigrateResult(state, 'test.tmp', timedelta(0))

    def test_migrate_result_displaced(self):

        result = MigrateResult(MigrateState.DISPLACED, 'test.tmp', timedelta(minutes=1, seconds=13))
        self.assertEqual(result.__str__(), 'DISPLACED|test.tmp|0:01:13||')

        result = MigrateResult(MigrateState.DISPLACED, 'test.tmp', timedelta(minutes=1, seconds=13), 4, 67)
        self.assertEqual(result.__str__(), 'DISPLACED|test.tmp|0:01:13|4|67')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtilsMigration.create_migrate_result_with_no_filename(MigrateState.DISPLACED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtilsMigration.create_migrate_result_with_no_time_elapsed(MigrateState.DISPLACED)

    def test_migrate_result_failed(self):

        result = MigrateResult(MigrateState.FAILED, 'test.tmp', timedelta(minutes=1, seconds=13), 783, 560, 'An error occured.')
        self.assertEqual(result.__str__(), 'FAILED|test.tmp|0:01:13|783|560|An error occured.')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtilsMigration.create_migrate_result_with_no_filename(MigrateState.FAILED)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtilsMigration.create_migrate_result_with_no_time_elapsed(MigrateState.FAILED)

        with self.assertRaises(LfsUtilsError):
            MigrateResult(MigrateState.FAILED, 'test.tmp', timedelta(0), error_msg='')

    def test_migrate_result_ignored(self):

        result = MigrateResult(MigrateState.IGNORED, 'test.tmp', timedelta(0))
        self.assertEqual(result.__str__(), 'IGNORED|test.tmp')

    def test_migrate_result_skipped(self):

        result = MigrateResult(MigrateState.SKIPPED, 'test.tmp', timedelta(0))
        self.assertEqual(result.__str__(), 'SKIPPED|test.tmp')

    def test_migrate_result_success(self):

        result = MigrateResult(MigrateState.SUCCESS, 'test.tmp', timedelta(minutes=1, seconds=13))
        self.assertEqual(result.__str__(), 'SUCCESS|test.tmp|0:01:13||')

        result = MigrateResult(MigrateState.SUCCESS, 'test.tmp', timedelta(minutes=1, seconds=13), 4, 67)
        self.assertEqual(result.__str__(), 'SUCCESS|test.tmp|0:01:13|4|67')

        with self.assertRaises(LfsUtilsError):
            TestLfsUtilsMigration.create_migrate_result_with_no_filename(MigrateState.SUCCESS)

        with self.assertRaises(LfsUtilsError):
            TestLfsUtilsMigration.create_migrate_result_with_no_time_elapsed(MigrateState.SUCCESS)

    def test_migrate_result_creation(self):

        with self.assertRaises(LfsUtilsError):
            MigrateResult(None, 'test.tmp', timedelta(0))

        with self.assertRaises(LfsUtilsError):
            MigrateResult(MigrateState.SUCCESS, None, timedelta(0))

        with self.assertRaises(LfsUtilsError):
            MigrateResult(MigrateState.SUCCESS, 'test.tmp', None)
