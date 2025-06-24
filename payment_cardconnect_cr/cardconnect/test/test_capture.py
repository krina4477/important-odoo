# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import cardconnect # noqa
from cardconnect.test.helper import (
    CardConnectTest
)

TEST_CAPTURE = {
    'merchid': '496160873888',
    'retref': '109858246936'
}


class CaptureTest(CardConnectTest): # noqa

    def test_capture_create(self): # noqa
        cardconnect.Capture.create(**TEST_CAPTURE)

        self.requestor_mock.request.assert_called_with(
            'put',
            '/capture',
            TEST_CAPTURE
        )
