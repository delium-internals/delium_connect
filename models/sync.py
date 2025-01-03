from odoo import *
import telnetlib


class Sync(models.Model):
  _name = "odoo.sync"
  _description = "Sync module to sync data to Delium"

  odoo_host = fields.Char(string="Odoo Host", required=True)
  dcove_tunnel = fields.Char(string="DCove Tunnel URL", required=True)
  sync_token = fields.Char(string="Sync Token Given by the Delium team for integration", required=True)
  database_pass = fields.Char(string="Api Key from odoo", required=True)
  database_user = fields.Char(string="Database User", required=True)
  database_name = fields.Char(string="Database name", required=True)
  store_ids = fields.Many2many('stock.warehouse', 'odoo_sync_stores_rel', 'config_id', 'warehouse_id', string="Stores to Sync", required=True)

  @api.model
  def read(self, fields=None, load='_classic_read'):
    records = super(Sync, self).read(fields, load)
    for res in records:
      res['database_pass'] = ''  # Set blank value for editing
      res['sync_token'] = ''  # Set blank value for editing
    return records

  def write(self, vals):
    result = super(Sync, self).write(vals)
    self._register_client_to_dcove_tunnel(vals)
    return result

  def _register_client_to_dcove_tunnel(self, vals):
    telnet_host, telnet_port = vals['dcove_tunnel'].split(" ")



