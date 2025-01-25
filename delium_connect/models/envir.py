from odoo import _
from odoo import *
from odoo.addons.delium_connect.utils import logger
from odoo.exceptions import ValidationError

class DeliumEnvironment(models.Model):
  _name = "delium.environment"
  _description = "Config to switch between environments to Delium's infra"

  envir = fields.Selection(string="Envir", required=True, default="dev", selection=[('dev', 'dev'), ('qa', 'qa'), ('prod', 'prod')])

  @api.model
  def create(self, vals):
    logger.info("[delium.environemnt] [Create] Running create method ...")
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT * FROM delium_environment """)
    result = self.env.cr.fetchone()

    if result is not None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Environment config already exists."),
        "message": _("You can have only one environment config."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("You can have only one config for the environment.")
