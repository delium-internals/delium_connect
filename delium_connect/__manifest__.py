{
  "name": "Delium Connect",
  "author": "DeliumTech",
  'summary': 'Integration app to allow syncing of data from Odoo to Delium.',
  'description': 'Integration app to allow syncing of data from Odoo to Delium.',
  'images': [
    'static/images/banner.png',
  ],
  'application': True,
  'installable': True,
  "version": "1.0.0",
  'depends': ['base', 'stock'],
  'website': 'https://delium.ai',
  'license': 'LGPL-3',
  "data": [
    "security/ir.model.access.csv",
    "views/css.xml",
    "views/subscribe.xml",
    "views/sync.xml",
    "views/env.xml",
    "views/main_menu.xml"
  ]
}