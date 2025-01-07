from odoo import *


class Sync(models.Model):
  _name = "delium.sync"
  _description = "Sync module to sync data to Delium"

  external_client_id = fields.Char(string="external_client_id", compute="_get_external_id_from_subscripion")
  odoo_host = fields.Char(string="Odoo Host", required=True)
  sync_token = fields.Char(string="Sync Token Given by the Delium team for integration", required=True)
  database_pass = fields.Char(string="Api Key from odoo", required=True)
  database_user = fields.Char(string="Database User", required=True)
  database_name = fields.Char(string="Database name", required=True)
  store_ids = fields.Many2many('stock.warehouse', 'odoo_sync_stores_rel', 'config_id', 'warehouse_id', string="Stores to Sync", required=True)

  def _get_external_id_from_subscripion(self):
    self.env.cr.execute("""SELECT external_client_id FROM delium_subscription """)
    result = self.env.cr.fetchone()
    if result is None:
      raise Exception("No subscription to Delium is done. You must first subscribe to Delium's The Miner.")
    for record in self:
      record.external_client_id = result[0]

  @api.model
  def read(self, fields=None, load='_classic_read'):
    records = super(Sync, self).read(fields, load)
    for res in records:
      res['database_pass'] = ''  # Set blank value for editing
      res['sync_token'] = ''  # Set blank value for editing
    return records

  @api.model
  def create(self, vals):
    subscription = self.env['delium.subscription'].browse(vals['external_client_id'])
    if not subscription.api_token:
      return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
            'title': 'Error',
            'message': 'No API token found for the subscription. Please subscribe and verify your subscription for the API token first.',
            'type': 'danger',
          }
        }
      # raise ValidationError("No API token found for the subscription. Please subscribe and verify your subscription for the API token.")
    else:
      vals['sync_token'] = subscription.api_token
    return super(Sync, self).create(vals)


  def write(self, vals):
    subscription = self.env['delium.subscription'].browse(vals['external_client_id'])
    if not subscription.api_token:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Error',
          'message': 'No API token found for the subscription. Please subscribe and verify your subscription for the API token first.',
          'type': 'danger',
        }
      }
      # raise ValidationError("No API token found for the subscription. Please subscribe and verify your subscription for the API token.")
    else:
      vals['sync_token'] = subscription.api_token
    return super(Sync, self).write(vals)






