# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import os # noqa
import unittest2


def all(): # noqa
    path = os.path.dirname(os.path.realpath(__file__))
    return unittest2.defaultTestLoader.discover(path)
