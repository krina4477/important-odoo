# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import cardconnect # noqa
from cardconnect.test.helper import (
    CardConnectTest
)

TEST_REFUND = {
    'merchid': '496160873888',
    'retref': '109858246936'
}


class RefundTest(CardConnectTest): # noqa

    def test_refund_create(self): # noqa
        cardconnect.Refund.create(**TEST_REFUND)

        self.requestor_mock.request.assert_called_with(
            'put',
            '/refund',
            TEST_REFUND
        )
