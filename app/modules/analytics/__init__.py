# -*- coding: utf-8 -*-
from flask import Blueprint
from app.modules.analytics import tiempo

mod_analytics = Blueprint('tiempo', __name__, url_prefix='/analytics')

mod_analytics.add_url_rule('/entradas_tiempo',
                           view_func=tiempo.entradas,
                           methods=['GET', 'POST'])
