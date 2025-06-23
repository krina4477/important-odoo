# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

try:
    from num2words import num2words
except ImportError:
    num2words = None


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_in_words = fields.Char(
        compute='_compute_amount_word', string='Amount in Words', readonly=True)
    print_to_report = fields.Boolean("Show in Report", default=True)
    sh_amount_to_word_in_upper_case = fields.Boolean(
        string="Upper-case amount in words", default=lambda self: self.env.company.sh_amount_to_word_in_upper_case)

    @api.depends("amount_total", "sh_amount_to_word_in_upper_case")
    def _compute_amount_word(self):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()
        if num2words is None:
            raise UserError(
                _("The num2words python library is not installed, amount-in-words features won't be fully available."))

        amount = self.amount_total
        currency = self.currency_id or self.env.company.currency_id

        formatted = "%.{0}f".format(currency.decimal_places) % amount or 0.0
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang = tools.get_lang(self.env, self.partner_id.lang or self.env.user.lang)
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=currency.currency_unit_label or "",
        )

        if not currency.is_zero(amount - integer_value):
            amount_words += ' ' + tools.ustr('{amt_separator} {amt_value} {amt_word}').format(
                amt_separator=currency.amount_separator or _("and"),
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word=currency.currency_subunit_label or "",

            )
        amount_words += ' ' + \
            tools.ustr('{amt_cft}').format(
                amt_cft=currency.close_financial_text or "")

        if self.sh_amount_to_word_in_upper_case:
            amount_words = amount_words.upper()

        self.amount_in_words = amount_words

        # language = 'en'
        # list_lang = [['en', 'en_US'], ['en', 'en_AU'],
        #              ['en', 'en_GB'], ['fr', 'fr_BE'],
        #              ['fr', 'fr_CA'], ['fr', 'fr_CH'],
        #              ['fr', 'fr_FR'], ['es', 'es_ES'],
        #              ['es', 'es_AR'], ['es', 'es_BO'],
        #              ['es', 'es_CL'], ['es', 'es_CO'],
        #              ['es', 'es_CR'], ['es', 'es_DO'],
        #              ['es', 'es_EC'], ['es', 'es_GT'],
        #              ['es', 'es_MX'], ['es', 'es_PA'],
        #              ['es', 'es_PE'], ['es', 'es_PY'],
        #              ['es', 'es_UY'], ['es', 'es_VE'],
        #              ['lt', 'lt_LT'], ['lv', 'lv_LV'],
        #              ['no', 'nb_NO'], ['pl', 'pl_PL'],
        #              ['ru', 'ru_RU'], ['dk', 'da_DK'],
        #              ['pt_BR', 'pt_BR'], ['de', 'de_DE'],
        #              ['de', 'de_CH'], ['ar', 'ar_SY'],
        #              ['it', 'it_IT'], ['he', 'he_IL'],
        #              ['id', 'id_ID'], ['tr', 'tr_TR'],
        #              ['nl', 'nl_NL'], ['nl', 'nl_BE'],
        #              ['uk', 'uk_UA'], ['sl', 'sl_SI'],
        #              ['vi_VN', 'vi_VN']]

        # cnt = 0
        # for rec in list_lang[cnt:len(list_lang)]:
        #     if rec[1] == self.partner_id.lang:
        #         language = rec[0]
        #     cnt += 1

        # decimal = self.currency_id.decimal_places

        # amount_str = str('{:2f}'.format(self.amount_total))
        # amount_str_splt = amount_str.split('.')

        # after_amount_words = ''
        # before_amount_words = ''

        # before_point_value = amount_str_splt[0]
        # after_point_value = amount_str_splt[1][:decimal]

        # if before_point_value:
        #     before_amount_words = num2words(int(before_point_value), lang=language)

        # if after_point_value:
        #     after_amount_words = num2words(int(after_point_value), lang=language)

        # amount = before_amount_words

        # if self.currency_id and self.currency_id.currency_unit_label:
        #     amount = amount + ' ' + self.currency_id.currency_unit_label

        # if self.currency_id and self.currency_id.amount_separator:
        #     amount = amount + ' ' + self.currency_id.amount_separator

        # amount = amount + ' ' + after_amount_words

        # if self.currency_id and self.currency_id.currency_subunit_label:
        #     amount = amount + ' ' + self.currency_id.currency_subunit_label

        # if self.currency_id and self.currency_id.close_financial_text:
        #     amount = amount + ' ' + self.currency_id.close_financial_text

        # self.amount_in_words = amount
