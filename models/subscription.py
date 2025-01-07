import requests

import json
from odoo import *
from odoo.addons.odeosync.logger import logger


proboscis_mapper = {
  'dev': 'https://qa.local:9090',
  'qa': 'https://proboscis.delium.dev/api',
  'prod': 'https://proboscis.delium.io/api'
}

class Subscription(models.Model):
  _name = "delium.subscription"
  _description = "Subscribe to Delium's The Miner"

  # default fields. not to be shown on form
  licensed_products = fields.Char(string="Licensed Products", required=True, default='The Eye', readonly=True)
  vendor_name = fields.Char(string="Vendor Name", required=True, default='odoo', readonly=True)
  product_name = fields.Char(string="Product Name", required=True, default='odoo', readonly=True)
  use_internal_auth = fields.Char(string="Use Internal Auth", required=True, default=True, readonly=True)
  licensing_stores = fields.Char(string="Licensing Stores", required=True, default='["*"]', readonly=True)
  envir = fields.Selection(string="Envir", required=True, default="prod", selection=[('dev', 'dev'), ('qa', 'qa'), ('prod', 'prod')])

  # Filled on response
  domain = fields.Char(string="Domain", readonly=True)
  api_token = fields.Char(string="Api Token", readonly=True)
  otp_validated = fields.Char(string="Otp Validated", default=False, readonly=True)
  otp_input = fields.Char(string="OTP: ")

  external_client_id = fields.Char(string="External Client Id", required=True)
  name = fields.Char(string="Name", required=True)
  vertical = fields.Selection(string="Vertical", required=True, selection=[('CPG', 'CPG'), ('CDIT', 'CDIT')], default='CPG')
  country = fields.Selection(string="Country", required=True, selection=[('INDIA', 'INDIA')], default='INDIA')
  user_name = fields.Char(string="User Name", required=True)
  user_phone = fields.Char(string="User Phone", required=True)
  user_email = fields.Char(string="User Email", required=True)
  billing_address = fields.Char(string="Billing Address", required=True)
  billing_number = fields.Char(string="Billing Number", required=True)
  billing_email = fields.Char(string="Billing Email", required=True)
  tax_name = fields.Selection(string="Tax Name", required=True, selection=[('GST_L', 'GST_L'), ('GST_R', 'GST_R')], default='GST_L')
  gst_no = fields.Char(string="Gst No", required=True)

  @api.onchange('env')
  def _onchange_env(self):
    """Update the proboscis_host field based on the environment selection."""
    self.proboscis_host = proboscis_mapper.get(self.envir, 'https://qa.local:9090')
    self.save()


  def prepare_request_body(self, vals):
    logger.info("======================")
    logger.info(f"Vals: {vals}")
    logger.info("======================")
    body = {
      "name": vals.get('name', self.name),
      "country": vals.get('country', self.country).upper(),
      "licensedProducts": vals.get('licensed_products', self.licensed_products),
      "productName": vals.get('product_name', self.product_name),
      "vendorName": vals.get('vendor_name', self.vendor_name),
      "vertical": vals.get('vertical', self.vertical),
      "useInternalAuth": vals.get('use_internal_auth', self.use_internal_auth),
      "userName": vals.get('user_name', self.user_name),
      "userPhone": vals.get('user_phone', self.user_phone),
      "userEmail": vals.get('user_email', self.user_email),
      "externalClientId": f"odoo{vals.get('external_client_id', self.external_client_id)}",
      "countryCode": vals.get('country', self.country)[:2].upper(),
      "licensingStores": vals.get('licensing_stores', self.licensing_stores),
      "billingAddress": vals.get('billing_address', self.billing_address),
      "billingNumber": vals.get('billing_number', self.billing_number),
      "billingEmail": vals.get('billing_email', self.billing_email),
      "taxName": vals.get('tax_name', self.tax_name),
      "gstNo": vals.get('gst_no', self.gst_no)
    }
    logger.info(f"Body: {body}")
    return body

  @api.model
  def create(self, vals):
    # Set defaults
    vals['licensed_products'] = 'The Eye'
    vals['vendor_name'] = 'odoo'
    vals['product_name'] = 'odoo'
    vals['use_internal_auth'] = True
    vals['licensing_stores'] = '["*"]'

    request_body = self.prepare_request_body(vals)
    headers = {'Content-Type': 'application/json'}
    proboscis_host = proboscis_mapper.get(self.envir, 'https://qa.local:9090')
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/create", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      self.env['ir.actions.client'].notify({
        'title': f'Subsciption request recorded. Verification Pending',
        'message': f'Please check your email {self.user_email} for the OTP. Upon verification, your subscription will be complete.',
        'type': 'info',
      })
      response_body = res.json()
      vals['domain'] = response_body['domain']
      vals['otp_validated'] = False
      self.env['ir.actions.client'].reload()
    else:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Subsciption request failed.',
          'message': 'Please contact support for help.',
          'type': 'danger',
        }
      }
    return super(Subscription, self).create(vals)

  @api.model
  def write(self, vals):
    request_body = self.prepare_request_body(vals)
    headers = {'Content-Type': 'application/json'}
    proboscis_host = proboscis_mapper.get(self.envir, 'https://qa.local:9090')
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/create", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      response_body = res.json()
      self.env['ir.actions.client'].notify({
        'title': f'Welcome back. Thank you for subscribing again. Verification is pending',
        'message': f'Please check your email {self.user_email} for the OTP. Upon verification, your subscription will be complete.',
        'type': 'info',
      })
      vals['domain'] = response_body['domain']
      vals['otp_validated'] = False
      self.env['ir.actions.client'].reload()
    else:
      response_body = res.json()
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Subscription request failed.',
          'message': response_body['message'],
          'type': 'danger',
        }
      }
    return super(Subscription, self).write(vals)

  def resend_otp(self):
    if not self.domain:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Cannot Send OTP',
          'message': 'OTP for verification can be sent only after subscription. Save the subscription details to begin the verification.',
          'type': 'danger',
        }
      }
    proboscis_host = proboscis_mapper.get(self.envir, 'https://qa.local:9090')
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/${self.domain}/{self.user_phone}/resend_otp", verify=False)
    if res.status_code == 200:
      return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
            'title': f'OTP Sent to your email {self.user_email}',
            'message': 'Please check your email for the OTP',
            'type': 'info',
          }
        }
    else:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Failed to send OTP.',
          'message': 'Please contact support.',
          'type': 'danger',
        }
      }

  def verify_otp(self):
    request_body = self.prepare_request_body()
    headers = {'Content-Type': 'application/json'}
    res = requests.post(f"{self.proboscis_host}/ext/ephemeral_client/{self.domain}/{self.user_phone}/{self.otp_input}", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      response_body = res.json()
      self.api_token = response_body['apiToken']
      # There's no need to explicitly call self.save() unless you want to force a save immediately.
      self.save()
      return {
        'type': 'ir.actions.client',
        'tag': 'reload',
      }
    else:
      response_body = res.json()
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'OTP verification failed',
          'message': response_body['message'],
          'type': 'danger',
        }
      }

