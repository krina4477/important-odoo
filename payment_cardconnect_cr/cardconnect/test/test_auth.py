# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import cardconnect # noqa
from cardconnect.test.helper import (
    CardConnectTest
)

TEST_AUTH = {
    'merchid': '496160873888',
    'account': '4111111111111111',
    'expiry': '1218',
    'amount': '1.00',
    'currency': 'USD'
}


class AuthTest(CardConnectTest): # noqa

    def test_auth_create(self): # noqa
        cardconnect.Auth.create(**TEST_AUTH)

        self.requestor_mock.request.assert_called_with(
            'put',
            '/auth',
            TEST_AUTH
        )
