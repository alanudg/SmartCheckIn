# -*- coding: utf-8 -*-
from app.models import Ocupacion, Lugar, Computadora, Registro, Usuario, Rol
from app.admin.model_views import ComputadoraAdmin, LugarAdmin, \
                                  OcupacionAdmin, UserAdmin, RoleAdmin, \
                                  RegistroAdmin


def load_model_views(admin, db_sql):
    admin.add_view(UserAdmin(Usuario, db_sql.session))
    admin.add_view(RoleAdmin(Rol, db_sql.session))
    admin.add_view(OcupacionAdmin(Ocupacion, db_sql.session))
    admin.add_view(LugarAdmin(Lugar, db_sql.session))
    admin.add_view(ComputadoraAdmin(Computadora, db_sql.session))
    admin.add_view(RegistroAdmin(Registro, db_sql.session))
