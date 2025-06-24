# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import cardconnect # noqa
from cardconnect.test.helper import (
    CardConnectTest
)

TEST_VOID = {
    'merchid': '496160873888',
    'retref': '109858246936'
}


class VoidTest(CardConnectTest): # noqa

    def test_void_create(self): # noqa
        cardconnect.Void.create(**TEST_VOID)

        self.requestor_mock.request.assert_called_with(
            'put',
            '/void',
            TEST_VOID
        )
