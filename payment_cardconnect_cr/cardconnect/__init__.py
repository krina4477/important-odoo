# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
# https://developer.cardconnect.com/cardconnect-api # noqa

username = None
password = None
base_url = None
debug = False

from .service import ( # noqa
    Auth,
    Capture,
    Void,
    Refund,
    Funding,
    Profile,
    SigCap)

from .error import ( # noqa
    ApiError,
    ApiConnectionError,
    ApiAuthenticationError,
    ApiRequestError,
    CardConnectError)

from .api_requestor import ApiRequestor # noqa

from .service import ( # noqa
    ApiResource,
    CreateableApiResource,
    UpdateableApiResource,
    DeletableApiResource)

from .util import json, logger # noqa
