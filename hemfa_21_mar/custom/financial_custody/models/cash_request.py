from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError  # Import ValidationError
import logging
from datetime import timedelta  # Add this import

_logger = logging.getLogger(__name__)


class CashRequest(models.Model):
    _name = 'financial.custody.request'
    _description = 'Cash Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Inherit for notifications and activities

    name = fields.Char(string="Request Reference", required=True, copy=False, readonly=True, default='New', tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Requested By", default=lambda self: self.env.user.employee_id.id, tracking=True)
    amount = fields.Float(string="Requested Amount", required=True, tracking=True)
    description = fields.Text(string="Description", required=True, tracking=True)
    
    custody_type = fields.Selection([('permanent', 'Permanent - مستديمة'), ('temporary', 'Temporary - مؤقتة')],
                                    string="Custody Type", required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)

    custody_account_id = fields.Many2one('account.account', string="Custody Account", compute='_compute_custody_account', readonly=True, tracking=True)
    
    journal_id = fields.Many2one('account.journal', string="Journal", domain="[('type', '=', 'cash')]", tracking=True)
    move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True, tracking=True)
    reconcile_move_id = fields.Many2one('account.move', string="Reconciliation Journal Entry", readonly=True, tracking=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company, tracking=True)

    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),
                              ('declined', 'Declined'), ('cancelled', 'Cancelled'), ('cashed', 'Cashed'),
                              ('expense_report', 'Expense Report'), ('reconciled', 'Reconciled')],
                             default='draft', tracking=True)
    
    date_request = fields.Date(string="Date of Request", readonly=True, tracking=True)
    date_approve = fields.Date(string="Date of Approval", readonly=True, tracking=True)
    date_cashed = fields.Date(string="Date of Collection", readonly=True, tracking=True)
    
    requested_by_user = fields.Many2one('res.users', string="Requested By", readonly=True, tracking=True)
    approved_by_user = fields.Many2one('res.users', string="Approved By", readonly=True, tracking=True)
    cashed_by_user = fields.Many2one('res.users', string="Cashed By", readonly=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, tracking=True)
    decline_reason = fields.Text(string="Reason for Decline", readonly=True, tracking=True)
    expense_report_id = fields.Many2one('financial.custody.expense.report', string="Expense Report", readonly=True, tracking=True)
    expense_line_ids = fields.One2many('financial.custody.expense.report.line', 'cash_request_id', string="Expense Lines", tracking=True)
    total_expense = fields.Float(string="Total Amount", compute='_compute_total_expense', store=True, tracking=True)
    purchase_line_ids = fields.One2many('financial.custody.purchase.line', 'cash_request_id', string="Purchase Lines", tracking=True)
    total_purchase_payment = fields.Monetary(string="Total Purchase Payment", compute='_compute_total_purchase_payment', store=True, currency_field='currency_id', tracking=True)
    total_spent = fields.Float(string="Total Spent", compute="_compute_total_spent", readonly=True, tracking=True)
    custody_difference = fields.Float(string="Custody Difference", compute='_compute_custody_difference', tracking=True)
    amount_req = fields.Float(string="Amount Req", readonly=True, compute='_compute_req_amount', tracking=True)
    payment_ids = fields.One2many('account.payment', 'custody_request_id', string="Related Payments", readonly=True, tracking=True)
    payment_count = fields.Integer(string="Payment Count", compute='_compute_payment_count', tracking=True)
    total_paid = fields.Float(compute="_compute_total_paid", string="Total Paid", readonly=True, tracking=True)
    remaining_amount_to_pay = fields.Float(string="Remaining Amount to Pay", compute="_compute_remaining_amount_to_pay", readonly=True, tracking=True)
    remaining_amount_to_receive = fields.Float(string="Remaining Amount to Receive", compute="_compute_remaining_amount_to_receive", readonly=True, tracking=True)
    previous_remaining_amount = fields.Float(string="Previous Custody Remaining Amount", readonly=True, tracking=True)
    requested_amount = fields.Float(string="Requested Amount", required=True, tracking=True)
    linked_request_count = fields.Integer(string="Linked Request Count", compute='_compute_linked_request_count', tracking=True)
    linked_cash_request_ids = fields.One2many('financial.custody.request', 'linked_cash_request_id', string="Linked Cash Requests", readonly=True, tracking=True)
    linked_cash_request_id = fields.Many2one('financial.custody.request', string="Linked Cash Request", readonly=True, tracking=True)
    

    @api.depends('payment_ids.state', 'payment_ids.amount')
    def _compute_total_paid(self):
        for rec in self:
            rec.total_paid = sum(payment.amount for payment in rec.payment_ids if payment.state == 'posted')


    @api.depends('custody_difference', 'total_paid')
    def _compute_remaining_amount_to_pay(self):
        for rec in self:
            if rec.custody_difference < 0:
                rec.remaining_amount_to_pay = abs(rec.custody_difference) - rec.total_paid
            else:
                rec.remaining_amount_to_pay = 0.0
    
    @api.depends('custody_difference', 'total_paid')
    def _compute_remaining_amount_to_receive(self):
        for rec in self:
            if rec.custody_difference > 0:
                rec.remaining_amount_to_receive = rec.custody_difference - rec.total_paid
            else:
                rec.remaining_amount_to_receive = 0.0

        
    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)
    

    @api.depends('amount', 'amount_req')
    def _compute_req_amount(self):
        for rec in self:
            rec.amount_req = rec.amount + rec.previous_remaining_amount

    @api.depends('amount', 'total_spent')
    def _compute_custody_difference(self):
        for rec in self:
            rec.custody_difference = rec.amount_req - rec.total_spent

    @api.depends('linked_cash_request_id')
    def _compute_linked_request_count(self):
        for rec in self:
            rec.linked_request_count = self.env['financial.custody.request'].search_count([('linked_cash_request_id', '=', rec.id)])

    def action_pay_to_employee(self):
        
        if self.remaining_amount_to_pay <= 0:
                    raise ValidationError("No further payment required. The full custody difference has already been paid.")
        
        # Ask the user for the amount to pay
        amount_to_pay = self.remaining_amount_to_pay  # or modify this to ask for user input

        if amount_to_pay > self.remaining_amount_to_pay:
            raise ValidationError(f"You cannot pay more than {self.remaining_amount_to_pay}.")
        

        if any(payment.state == 'draft' for payment in self.payment_ids):
            raise ValidationError("A payment is still in draft state. Confirm or delete the payment before creating a new one.")
        
        
        payment_vals = {
            'payment_type': 'outbound',  # Outbound payment to employee
            'partner_id': self.employee_id.user_id.partner_id.id,  # Ensure this is correct
            'amount': amount_to_pay,
            'ref': f'{self.name} - Settlement',  # Reference number with Settlement
            'journal_id': self.journal_id.id,  # Ensure journal is set correctly
            'date': fields.Date.today(),  # Set the current date for the payment
            'custody_request_id': self.id,
            'is_cash_request_related': True,  # Set the flag to true
            'destination_account_id': self.custody_account_id.id,  # Passing the custody account as the destination account
        }

        payment = self.env['account.payment'].create(payment_vals)
        # Log a message in the chatter
        self.message_post(body=f"Payment of {amount_to_pay} created in draft.")

        # Recompute fields after payment creation (to update totals)
        self._compute_total_paid()
        self._compute_remaining_amount_to_pay()


    def action_receive_from_employee(self):

        if self.remaining_amount_to_receive <= 0:
            raise ValidationError("No further payment required. The full custody difference has already been received.")
        
        # Check if any draft payments exist to prevent new payments until the existing draft is confirmed
        if any(payment.state == 'draft' for payment in self.payment_ids):
            raise ValidationError("A payment is still in draft state. Confirm or delete the payment before creating a new one.")
        
        # Ask the user for the amount to receive
        amount_to_receive = self.remaining_amount_to_receive  # or modify this to ask for user input
        if amount_to_receive > self.remaining_amount_to_receive:
            raise ValidationError(f"You cannot receive more than {self.remaining_amount_to_receive}.")
        
        payment_vals = {
            'payment_type': 'inbound',  # Inbound payment from employee
            'partner_id': self.employee_id.user_id.partner_id.id,  # Ensure this is correct
            'amount': amount_to_receive,
            'ref': f'{self.name} - Settlement',  # Reference number with Settlement
            'journal_id': self.journal_id.id,  # Ensure journal is set correctly
            'date': fields.Date.today(),  # Set the current date for the payment
            'custody_request_id': self.id,
            'is_cash_request_related': True,  # Set the flag to true
            'destination_account_id': self.custody_account_id.id,  # Passing the custody account as the destination account
        }

        payment = self.env['account.payment'].create(payment_vals)
        self.message_post(body=f"Payment of {amount_to_receive} received from employee in draft.")
        self._compute_total_paid()
        self._compute_remaining_amount_to_receive()
    
    def action_custody_recompensation(self):
         _logger.info("Custody recompensation button clicked.")

         for rec in self:
             # Check if there are any linked cash requests in draft state
             draft_linked_requests = self.env['financial.custody.request'].search([
                 ('linked_cash_request_id', '=', rec.id),
                 ('state', '=', 'draft')
             ])

             if draft_linked_requests:
                 raise ValidationError(_("There is a linked cash request in draft state. Please review and either continue or delete the draft request before proceeding."))
             # Check if there is a linked cash request in a state other than draft
             non_draft_linked_requests = self.env['financial.custody.request'].search([
                 ('linked_cash_request_id', '=', rec.id),
                 ('state', '!=', 'draft')
             ])
             if non_draft_linked_requests:
                 raise ValidationError(_("There is already a linked cash request that is not in draft state. You cannot create another cash request."))
             
             # Proceed if no draft linked requests are found
             if rec.custody_type == 'permanent':
                 # Check if total spent is at least equal to the required percentage
                 required_spent_amount = (rec.amount_req * rec.company_id.custody_recompensation_percentage) / 100
                 if rec.total_spent >= required_spent_amount:
                     _logger.info("Proceeding with custody recompensation.")
                     # Proceed with custody recompensation
                     rec.create_new_cash_request()
                 else:
                     raise ValidationError("You cannot proceed with the recompensation. The total spent must be at least equal to {}% of the requested amount.".format(rec.company_id.custody_recompensation_percentage))
             else:
              _logger.info("Custody type is not permanent, skipping recompensation.")
    
    def create_new_cash_request(self):
        for rec in self:
            new_requested_amount = rec.total_spent or rec.amount_req or rec.amount

            if not new_requested_amount:
                raise ValidationError(_("Requested amount cannot be empty."))
            
            # Create a new cash request with the remaining amount
            new_cash_request = self.env['financial.custody.request'].create({
                'requested_amount': new_requested_amount,
                'amount': new_requested_amount,
                'custody_type': rec.custody_type,  # Keep the same type
                'previous_remaining_amount': rec.custody_difference,  # Store the remaining from previous request
                'linked_cash_request_id': rec.id,  # Link the new cash request to the current one
                'amount_req': rec.amount_req or rec.amount + rec.custody_difference,
                'description': rec.description,  # Pass the description to the new request
            })

            # Log a message to indicate the creation of the new cash request
            rec.message_post(body=f"A new cash request {new_cash_request.name} has been created and linked to {rec.name}.")

            # Add the new linked request to the `linked_cash_request_ids`
            rec.linked_cash_request_ids = [(4, new_cash_request.id)]

    @api.depends('expense_line_ids.amount')
    def _compute_total_expense(self):
        for request in self:
            total = sum(line.amount for line in request.expense_line_ids)
            request.total_expense = total

    @api.depends('purchase_line_ids.amount_to_pay')  # Assuming `purchase_line_ids` exists and has an amount_to_pay field
    def _compute_total_purchase_payment(self):
        for request in self:
            total = sum(line.amount_to_pay for line in request.purchase_line_ids)
            request.total_purchase_payment = total

    @api.depends('total_expense', 'total_purchase_payment')
    def _compute_total_spent(self):
        for record in self:
            record.total_spent = record.total_expense + record.total_purchase_payment
    
    @api.depends('custody_type')
    def _compute_custody_account(self):
        for rec in self:
            if rec.custody_type == 'permanent':
                rec.custody_account_id = rec.company_id.custody_account_id
            elif rec.custody_type == 'temporary':
                rec.custody_account_id = rec.company_id.custody_account_temp_id
            else:
                rec.custody_account_id = False

    def action_submit(self):
        if not self.employee_id:
            raise ValidationError("You cannot submit this request because you do not have an associated employee record.")
        if self.amount <= 0:
            raise ValidationError("The requested amount cannot be zero or less.")
        
        self.write({
            'state': 'submitted',
            'date_request': fields.Date.today(),
            'requested_by_user': self.env.user.id,
        })
        self.message_post(body="Cash Request Submitted.")
        # Create an activity for the Approver group
        approver_group = self.env.ref('financial_custody.group_cash_request_approver')
        # Find a user in the Approver group to assign the activity
        approvers = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        if approvers:
            for approver in approvers:
                self.activity_schedule(
                    activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                    summary="Review Cash Request",
                    user_id=approver.id,
                    note=f"A new cash request {self.name} has been submitted for your review.",
                    date_deadline=fields.Date.today() + timedelta(days=3),  # Set deadline to 3 days from submission
                )

    def action_approve(self):
        self.write({
            'state': 'approved',
            'date_approve': fields.Date.today(),
            'approved_by_user': self.env.user.id,
        })
        self.message_post(body="Cash Request Approved.")

        # Create an activity for the Treasury group
        treasury_group = self.env.ref('financial_custody.group_treasury')
        # Find users in the Treasury group to assign the activity
        treasury_users = self.env['res.users'].search([('groups_id', 'in', treasury_group.id)])
        if treasury_users:
            for treasury_user in treasury_users:
                self.activity_schedule(
                    activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                    summary="Process Cash Request",
                    user_id=treasury_user.id,
                    note=f"The cash request {self.name} has been approved and requires treasury action.",
                    date_deadline=fields.Date.today() + timedelta(days=3),  # Set deadline to 3 days from approval
                )

    def action_decline(self):
        self.write({'state': 'declined'})
        self.message_post(body="Cash Request Declined.")
        # Notify the Requested By user
        if self.employee_id.user_id:
            self.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="Your Cash Request has been declined",
                user_id=self.employee_id.user_id.id,  # Notify the user who made the request
                note=f"The cash request {self.name} has been declined.",
                date_deadline=fields.Date.today() + timedelta(days=1),  # Set deadline to 1 day from decline date
            )

    def action_cancel(self):
        if self.move_id and self.move_id.state == 'draft':
            self.move_id.with_context(from_cash_request=True).button_cancel()
            self.message_post(body="Cashed Journal Entry Cancelled.")
        if self.reconcile_move_id and self.reconcile_move_id.state == 'draft':
            self.reconcile_move_id.with_context(from_cash_request=True).button_cancel()
            self.message_post(body="Reconciled Journal Entry Cancelled.")

        self.write({'state': 'cancelled'})
        self.message_post(body="Cash Request Cancelled.")
        # Notify the Requested By user
        if self.employee_id.user_id:
            self.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="Your Cash Request has been cancelled",
                user_id=self.employee_id.user_id.id,  # Notify the user who made the request
                note=f"The cash request {self.name} has been cancelled.",
                date_deadline=fields.Date.today() + timedelta(days=1),  # Set deadline to 1 day from cancel date
            )

    def action_reset_to_draft_cashed(self):
        self.ensure_one()

        if self.state != 'cashed':
            raise UserError(_("You can only reset to draft from the Cashed stage."))

        if self.move_id and self.move_id.state == 'posted':
            _logger.info("Resetting journal entry to draft for move_id: %s", self.move_id.id)
            self.move_id.with_context(from_cash_request=True).button_draft()
        
        if self.move_id.state != 'draft':
            raise UserError(_("The journal entry could not be reset to draft. Please check the journal entry."))
        else:
             _logger.info("Journal entry successfully reset to draft for move_id: %s", self.move_id.id)
        
        self.write({'state': 'draft'})
        self.message_post(body="The Cash Request has been reset to Draft from the Cashed stage.")


    def action_reset_to_draft_reconciled(self):
        self.ensure_one()
        if self.payment_ids:
            raise UserError(_("You cannot reset to draft because there are linked payments."))

        linked_requests = self.env['financial.custody.request'].search([
            ('linked_cash_request_id', '=', self.id),
        ])

        if linked_requests:
            raise UserError(_("You cannot reset to draft because there are related new cash requests."))
            
        if self.state != 'reconciled':
            raise UserError(_("You can only reset to draft from the Reconciled stage."))

        if self.reconcile_move_id and self.reconcile_move_id.state == 'posted':
            _logger.info("Resetting reconciliation journal entry to draft for move_id: %s", self.reconcile_move_id.id)
            self.reconcile_move_id.with_context(from_cash_request=True).button_draft()

        if self.reconcile_move_id.state != 'draft':
            raise UserError(_("The reconciliation journal entry could not be reset to draft. Please check the journal entry."))


        self.write({'state': 'expense_report'})
        self.message_post(body="The Cash Request has been reset to the Expense Report stage from the Reconciled stage.")

        if sum(self.reconcile_move_id.line_ids.mapped('debit')) != sum(self.reconcile_move_id.line_ids.mapped('credit')):
            raise UserError(_("The journal entry is not balanced. Please ensure debit equals credit."))
        _logger.info("Reconciliation journal entry successfully reset to draft for move_id: %s", self.reconcile_move_id.id)


    def action_reset_payments_to_draft(self):
        self.ensure_one()
        # Check if there are payments linked to this custody request
        if not self.payment_ids:
            raise UserError(_("There are no linked payments to reset."))
        # Loop through payments and reset their journal entries to draft
        for payment in self.payment_ids:
            if payment.state != 'posted':
                raise UserError(_("Only posted payments can be reset to draft."))
            
            # Check the journal entry of the payment and reset it to draft if it exists
            if payment.move_id and payment.move_id.state == 'posted':
                _logger.info("Resetting journal entry to draft for payment: %s", payment.id)
                
                payment.move_id.with_context(from_cash_request=True).button_draft()
            payment.state = 'draft'
            self.message_post(body="Payment reset to draft.")
        _logger.info("All payments linked to custody request %s have been reset to draft.", self.name)


    def update_journal_entry(self):
        if not self.move_id:
            raise UserError("No journal entry found for this cash request.")

        move_vals = {
            'journal_id': self.journal_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.custody_account_id.id,
                    'debit': self.amount,
                    'partner_id': self.employee_id.user_id.partner_id.id
                }),
                (0, 0, {
                    'account_id': self.journal_id.default_account_id.id, 
                    'credit': self.amount, 
                    'partner_id': self.employee_id.user_id.partner_id.id
                }),
           ],
           'is_cash_request_related': True,  # Set the flag to true
           'ref': self.name,
        }
        # Update the existing journal entry with the new values
        self.move_id.line_ids.unlink()  # Remove existing lines
        self.move_id.write(move_vals)  # Write the new values to the existing journal entry

        # Check if the entry is balanced
        total_debit = sum(self.move_id.line_ids.mapped('debit'))
        total_credit = sum(self.move_id.line_ids.mapped('credit'))
        if total_debit != total_credit:
            raise UserError("The journal entry is not balanced after the update. Debit: %s, Credit: %s" % (total_debit, total_credit))

        if self.move_id.state == 'draft':
            self.move_id.with_context(from_cash_request=True).action_post()  # Use the context when posting
        self.message_post(body="Journal entry updated successfully.")


    def action_cashed(self):
        if self.move_id:  # If the journal entry exists, update it
            self.update_journal_entry()
        else:
            self.create_journal_entry()  # Otherwise, create a new journal entry
        self.write({
            'state': 'cashed',
            'date_cashed': fields.Date.today(),
            'cashed_by_user': self.env.user.id,
        })
        self.message_post(body="Cash Request Cashed.")
        if self.employee_id.user_id:
            self.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="Your Cash Request has been cashed",
                user_id=self.employee_id.user_id.id,  # Notify the user who made the request
                note=f"The cash request {self.name} has been cashed.",
                date_deadline=fields.Date.today() + timedelta(days=1),  # Set deadline to 1 day from cashed date
            )

    def create_journal_entry(self):
        if not self.move_id:
            if not self.journal_id.default_account_id:
                raise UserError('Please configure the default account for the journal.')

            move_vals = {
                'journal_id': self.journal_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.custody_account_id.id, 
                        'debit': self.amount, 
                        'partner_id': self.employee_id.user_id.partner_id.id
                    }),
                    (0, 0, {
                        'account_id': self.journal_id.default_account_id.id, 
                        'credit': self.amount, 
                        'partner_id': self.employee_id.user_id.partner_id.id
                    }),
                ],
                'is_cash_request_related': True,  # Set the flag to true
                'ref': self.name,
            }
            move = self.env['account.move'].create(move_vals)
            move.with_context(from_cash_request=True).action_post()  # Use the context when posting
            self.move_id = move
        else:
            self.update_journal_entry()

        self.message_post(body="Journal entry created or updated successfully.")

    def action_view_journal_entry(self):
        self.ensure_one()
        if self.move_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cashed Journal Entry',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.move_id.id,
                'view_id': self.env.ref('account.view_move_form').id,
                'target': 'current',
            }

    def action_submit_expense_report(self):
        # Check if there are no expense lines or purchase lines
        if not self.expense_line_ids and not self.purchase_line_ids:
            raise ValidationError("You must add at least one expense or purchase line before submitting the expense report.")

        # Check if any expense line amount is zero or less
        for line in self.expense_line_ids:
            if line.amount <= 0:
                raise ValidationError("Expense line amount cannot be zero or less. Please review the expenses.")

        # Check if any purchase line amount to pay is zero or less
        for line in self.purchase_line_ids:
            if line.amount_to_pay <= 0:
                raise ValidationError("Purchase line 'Amount to Pay' cannot be zero or less. Please review the purchases.")
    
        # If no expense report exists, create one linked to the current cash request
        if not self.expense_report_id:
            expense_report = self.env['financial.custody.expense.report'].create({
                'cash_request_id': self.id,
            })
            self.expense_report_id = expense_report

        # Set the state to 'expense_report'
        self.write({'state': 'expense_report'})
        self.message_post(body="Expense Report Submitted.")
        # Notify the Manager group
        manager_group = self.env.ref('financial_custody.group_cash_request_manager')
    
        # Find users in the Manager group
        managers = self.env['res.users'].search([('groups_id', 'in', manager_group.id)])
    
        if managers:
            for manager in managers:
                self.activity_schedule(
                   activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                   summary="Review Expense Report",
                   user_id=manager.id,
                   note=f"An expense report for the cash request {self.name} has been submitted for your review.",
                   date_deadline=fields.Date.today() + timedelta(days=2),  # Set deadline to 2 days from submission
                )


    def action_undo_submit(self):
        """Roll back the state to 'Cashed' and allow editing of expense lines."""
        self.write({'state': 'cashed'})
        self.message_post(body="The expense report has been rolled back to 'Cashed' for further editing.")

    def action_reconcile(self):
        self.ensure_one()
        # Check if there are either expense lines or purchase lines
        if not self.expense_line_ids and not self.purchase_line_ids:
         raise UserError(_("No expense or purchase lines to reconcile."))
    
        # Check if the custody account is set
        if not self.custody_account_id:
         raise UserError(_("Custody Account is not set."))
    
        # Create or update reconciliation journal entry
        if self.reconcile_move_id:
         self.update_reconciliation_journal_entry()  # Update existing reconciliation entry
        else:
          self.create_reconciliation_journal_entry()  # Create new reconciliation journal entry

        # Automatically reconcile payment for each bill
        self._auto_reconcile_purchase_lines()

        # Set state to 'reconciled' and post message
        self.state = 'reconciled'
        self.message_post(body="Cash request has been reconciled.")
        # Notify the Requested By user
        if self.employee_id.user_id:
             self.activity_schedule(
                 activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                 summary="Your Cash Request has been reconciled",
                 user_id=self.employee_id.user_id.id,  # Notify the user who made the request
                 note=f"Your cash request {self.name} has been reconciled.",
                 date_deadline=fields.Date.today() + timedelta(days=1),  # Set deadline to 1 day from reconcile date
             )
    
        # Notify the Manager group
        manager_group = self.env.ref('financial_custody.group_cash_request_manager')
        managers = self.env['res.users'].search([('groups_id', 'in', manager_group.id)])
    
        if managers:
             for manager in managers:
                 self.activity_schedule(
                     activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                     summary="Cash Request Reconciled",
                     user_id=manager.id,
                     note=f"The cash request {self.name} has been reconciled.",
                     date_deadline=fields.Date.today() + timedelta(days=1),  # Set deadline to 1 day from reconcile date
                 )


    def create_reconciliation_journal_entry(self):
        # Ensure the default account is set for the journal
        if not self.journal_id.default_account_id:
         raise UserError('Please configure the default account for the journal.')
    
        move_vals = {
         'journal_id': self.journal_id.id,
         'date': fields.Date.today(),
         'ref': self.name,
         'line_ids': [],
         'is_cash_request_related': True,  # Set the flag to true
        }

        # Create debit lines for each expense line
        for line in self.expense_line_ids:
            move_vals['line_ids'].append((0, 0, {
               'account_id': line.expense_account_id.id,
               'name': line.reference,
               'debit': line.amount,
               'credit': 0.0,
               'partner_id': line.partner_id.id,
               'analytic_distribution': line.analytic_distribution,
            }))
   
        # Create debit lines for each purchase line (linked to bill)
        for purchase_line in self.purchase_line_ids:
            bill = purchase_line.bill_id
            if not bill:
                continue
            # Fetch the credit account from the bill's journal entry (usually the vendor's payable account)
            credit_line = bill.line_ids.filtered(lambda l: l.credit > 0)
            if not credit_line:
                raise UserError(_("No credit line found for bill %s.") % bill.name)
            
            move_vals['line_ids'].append((0, 0, {
             'account_id': credit_line[0].account_id.id,  # Using the first credit account found
             'name': _("Payment for bill %s") % bill.name,
             'debit': purchase_line.amount_to_pay,  # Amount to pay
             'credit': 0.0,
             'partner_id': bill.partner_id.id,
            }))

        # Create credit line for the custody account (total of expenses + purchases)
        total_credit = self.total_expense + sum(self.purchase_line_ids.mapped('amount_to_pay'))
        move_vals['line_ids'].append((0, 0, {
          'account_id': self.custody_account_id.id,
          'name': _("Custody Clearance for %s") % self.employee_id.name,
          'debit': 0.0,
          'credit': total_credit,
          'partner_id': self.employee_id.user_id.partner_id.id,
        }))

        # Create the journal entry and post it
        move = self.env['account.move'].create(move_vals)
        move.with_context(from_cash_request=True).action_post()
        self.reconcile_move_id = move
        self.message_post(body="Reconciliation journal entry created successfully.")

    def _auto_reconcile_purchase_lines(self):
         """Automatically reconcile the purchase lines linked to the bills with the journal entries created for this cash request."""
         for purchase_line in self.purchase_line_ids:
             bill = purchase_line.bill_id
             if not bill:
                 continue
             
             payable_lines = bill.line_ids.filtered(
                  lambda l: l.account_id.account_type == 'liability_payable' and
                            l.partner_id == purchase_line.partner_id and not l.reconciled
             )
             
             
             debit_amount_to_reconcile = purchase_line.amount_to_pay
             reconcile_debit_lines = self.reconcile_move_id.line_ids.filtered(
                 lambda l: l.debit == debit_amount_to_reconcile and
                           l.partner_id == purchase_line.partner_id and
                           not l.reconciled
             )
             
             _logger.info(f"Payable lines for bill {bill.name} and vendor {purchase_line.partner_id.name}: {payable_lines}")
             _logger.info(f"Debit lines for reconciliation for vendor {purchase_line.partner_id.name}: {reconcile_debit_lines}")

             
             # If there are payable and debit lines, reconcile them
             if payable_lines and reconcile_debit_lines:
                 lines_to_reconcile = payable_lines + reconcile_debit_lines
                 lines_to_reconcile.reconcile()
                 _logger.info(f"Reconciliation completed for bill {bill.name} and vendor {purchase_line.partner_id.name}.")
             else:
                _logger.warning(f"No matching payable or debit lines found for reconciliation of bill {bill.name} for vendor {purchase_line.partner_id.name}.")
             
    def update_reconciliation_journal_entry(self):
        if not self.reconcile_move_id:
           raise UserError("No reconciliation journal entry found for this cash request.")
    
        # Prepare the updated move values
        move_vals = {
           'journal_id': self.journal_id.id,
           'line_ids': [],
           'is_cash_request_related': True,  # Set the flag to true
        }

        # Create debit lines for each expense line
        for line in self.expense_line_ids:
           move_vals['line_ids'].append((0, 0, {
             'account_id': line.expense_account_id.id,
             'name': line.reference,
             'debit': line.amount,
             'credit': 0.0,
             'partner_id': line.partner_id.id,
             'analytic_distribution': line.analytic_distribution,
            }))

        # Create debit lines for each purchase line (linked to bill)
        for purchase_line in self.purchase_line_ids:
            bill = purchase_line.bill_id
            if not bill:
                continue
            # Fetch the credit account from the bill's journal entry (usually the vendor's payable account)
            credit_line = bill.line_ids.filtered(lambda l: l.credit > 0)
            if not credit_line:
                raise UserError(_("No credit line found for bill %s.") % bill.name)
            
            move_vals['line_ids'].append((0, 0, {
              'account_id': credit_line[0].account_id.id,  # Using the first credit account found
              'name': _("Payment for bill %s") % bill.name,
              'debit': purchase_line.amount_to_pay,  # Amount to pay
              'credit': 0.0,
              'partner_id': bill.partner_id.id,
            }))

        # Create the credit line for the custody account (total of expenses + purchases)
        total_credit = self.total_expense + sum(self.purchase_line_ids.mapped('amount_to_pay'))
        move_vals['line_ids'].append((0, 0, {
            'account_id': self.custody_account_id.id,
            'name': _("Custody Clearance for %s") % self.employee_id.name,
            'debit': 0.0,
            'credit': total_credit,
            'partner_id': self.employee_id.user_id.partner_id.id,
        }))

        # Remove the existing lines
        self.reconcile_move_id.line_ids.unlink()
    
        # Update the journal entry with the new values
        self.reconcile_move_id.write(move_vals)
    
        # Check if the journal entry is balanced
        if sum(self.reconcile_move_id.line_ids.mapped('debit')) != sum(self.reconcile_move_id.line_ids.mapped('credit')):
            raise UserError(_("The reconciliation journal entry is not balanced. Please ensure debit equals credit."))

        # Post the journal entry if it is in draft state
        if self.reconcile_move_id.state == 'draft':
             self.reconcile_move_id.with_context(from_cash_request=True).action_post()  # Pass the context here
    
        self.message_post(body="Reconciliation journal entry updated successfully.")

  
    def action_view_reconcile_journal_entry(self):
        self.ensure_one()
        if self.reconcile_move_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reconciliation Journal Entry',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.reconcile_move_id.id,
                'view_id': self.env.ref('account.view_move_form').id,
                'target': 'current',
            }
    
    def action_view_payment(self):
        if not self.payment_ids:
            raise UserError("No payment linked to this custody request.")
    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.payment_ids.ids)],
            'target': 'current',
        }
    
    def show_linked_requests(self):
        if not self.linked_cash_request_ids:
            raise UserError("No linked cash requests found.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linked Cash Requests',
            'res_model': 'financial.custody.request',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.linked_cash_request_ids.ids)],
            'target': 'current',
        }



    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You can only delete Cash Requests that are in the Draft state."))
            if rec.move_id or rec.reconcile_move_id:
                 raise UserError(_("You cannot delete this Cash Request because it has related journal entries. Please remove the journal entries first."))
                 
        return super(CashRequest, self).unlink()


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('financial.custody.request') or 'New'
        return super(CashRequest, self).create(vals)

    def _track_subtype(self, init_values):
       self.ensure_one()
       if 'state' in init_values and self.state == 'submitted':
          return self.env.ref('financial_custody.mt_cash_request_submitted')
       elif 'state' in init_values and self.state == 'approved':
          return self.env.ref('financial_custody.mt_cash_request_approved')
       elif 'state' in init_values and self.state == 'declined':
          return self.env.ref('financial_custody.mt_cash_request_declined')
       elif 'state' in init_values and self.state == 'cancelled':
          return self.env.ref('financial_custody.mt_cash_request_cancelled')
       return super(CashRequest, self)._track_subtype(init_values)

