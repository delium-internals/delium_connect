from odoo import _
from odoo import *
from odoo.addons.odeosync.utils import logger
from odoo.exceptions import ValidationError

class Sync(models.Model):
  _name = "delium.sync"
  _description = "Sync module to sync data to Delium"

  odoo_host = fields.Char(string="Odoo Host", required=True)
  sync_token = fields.Char(string="Sync Token Given by the Delium team for integration", required=True)
  database_pass = fields.Char(string="Api Key from odoo", required=True)
  database_user = fields.Char(string="Database User", required=True)
  database_name = fields.Char(string="Database name", required=True)
  store_ids = fields.Many2many('stock.warehouse', 'odoo_sync_stores_rel', 'config_id', 'warehouse_id', string="Stores to Sync", required=True)

  def fetch_subscription_details(self):
    logger.info("Here....")
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT external_client_id, domain, api_token FROM delium_subscription """)
    subscription_dict = self.env.cr.dictfetchone()
    if subscription_dict is None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subcsription details missing."),
        "message": _("No subscription to Delium is found. You must first subscribe and verify it for configuring the sync."),
        "sticky": False,
        "duration": 3000
      })
      return None, None, None
    return subscription_dict['external_client_id'], subscription_dict['domain'], subscription_dict['api_token']

  @api.model
  def read(self, fields=None, load='_classic_read'):
    records = super(Sync, self).read(fields, load)
    for res in records:
      res['database_pass'] = ''  # Set blank value for editing
      res['sync_token'] = ''  # Set blank value for editing
    return records

  @api.model
  def create(self, vals):
    logger.info(f"[delium.sync] [Create] Running create...")

    current_partner = self.env.user.partner_id

    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subcsription details missing."),
        "message": _("No API token found for the subscription. Please subscribe and verify your subscription for the API token first."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("No API token found for the subscription. Please subscribe and verify your subscription for the API token.")
    else:
      vals['sync_token'] = api_token
    return super(Sync, self).create(vals)


  def write(self, vals):
    logger.info(f"[delium.sync] [Write] Running write...")

    current_partner = self.env.user.partner_id

    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subcsription details missing."),
        "message": _("No API token found for the subscription. Please subscribe and verify your subscription for the API token first."),
        "sticky": False,
        "duration": 3000
      })
    else:
      vals['sync_token'] = api_token
    return super(Sync, self).write(vals)

