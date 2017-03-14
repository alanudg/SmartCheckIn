# -*- coding: utf-8 -*-
from flask import Blueprint
from app.modules.analytics import ATiempo

mod_analytics = Blueprint('tiempo', __name__, url_prefix='/analytics')

mod_analytics.add_url_rule('/')
