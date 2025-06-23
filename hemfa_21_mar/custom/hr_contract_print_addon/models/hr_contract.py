from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    amount_in_words = fields.Char(string="Amount in Words", compute="_compute_amount_in_words")
    amount_in_words_arabic = fields.Char(string="Amount in Words", compute="_compute_amount_in_words")

    @api.depends('wage')
    def _compute_amount_in_words(self):
        for record in self:
            record.amount_in_words = self.number_to_words(int(record.wage)) + " Libyan Dinar"
            record.amount_in_words_arabic = self.number_to_words_arabic(int(record.wage)) + " دينار ليبي"

    def number_to_words(self, number):
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
                 "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        if number == 0:
            return "Zero"

        words = ""
        if number // 1000 > 0:
            words += units[number // 1000] + " Thousand"
            number %= 1000
            if number > 0:
                words += " and "

        if number // 100 > 0:
            words += units[number // 100] + " Hundred"
            number %= 100
            if number > 0:
                words += " and "

        if number >= 10 and number < 20:
            words += teens[number - 10]
        else:
            if number // 10 > 0:
                words += tens[number // 10]
                number %= 10
                if number > 0:
                    words += "-"
            if number > 0:
                words += units[number]

        return words.strip()

    def number_to_words_arabic(self, number):
        units = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
        teens = ["عشرة", "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر",
                 "ثمانية عشر", "تسعة عشر"]
        tens = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
        hundreds = ["", "مائة", "مئتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]

        if number == 0:
            return "صفر"

        words = ""
        # Thousands
        if number // 1000 > 0:
            if number // 1000 == 1:
                words += "ألف"
            elif number // 1000 == 2:
                words += "ألفان"
            elif number // 1000 < 10:
                words += units[number // 1000] + " آلاف"
            else:
                words += units[number // 1000] + " ألف"
            number %= 1000
            if number > 0:
                words += " و "

        # Hundreds
        if number // 100 > 0:
            words += hundreds[number // 100]
            number %= 100
            if number > 0:
                words += " و "

        # Tens and Units (21-99)
        if number >= 10 and number < 20:
            words += teens[number - 10]
        else:
            if number % 10 > 0:
                words += units[number % 10]  # Units first in Arabic (for 21–99)
                if number // 10 > 1:
                    words += " و "
            if number // 10 > 1:
                words += tens[number // 10]

        return words.strip()
