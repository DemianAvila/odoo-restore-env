#!/bin/bash
source /src/.env

git clone https://github.com/odoo/odoo.git --depth 1 --branch ${ODOO_VERSION}