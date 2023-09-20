import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from datetime import datetime, timedelta
from modelos import db, Usuario, MenuSemana, Receta, Rol

from app import app


class TestMenuSemana(TestCase):
    def setUp(self) -> None:
        self.data_factory = Faker()
        self.client = app.test_client()

        nombre_usuario = "test_" + self.data_factory.name()
        contrasena = "T1$" + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode("utf-8")).hexdigest()

        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(
            usuario=nombre_usuario,
            contrasena=contrasena_encriptada,
            rol=Rol.ADMINISTRADOR,
        )
        db.session.add(usuario_nuevo)
        db.session.commit()

        usuario_login = {"usuario": nombre_usuario, "contrasena": contrasena}
        solicitud_login = self.client.post(
            "/login",
            data=json.dumps(usuario_login),
            headers={"Content-Type": "application/json"},
        )

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]

        self.menu_semana_creados = []
        self.recetas_creadas = []
        for i in range(3):
            self.crear_receta()

    def tearDown(self):
        for menu_creado in self.menu_semana_creados:
            menu = MenuSemana.query.get(menu_creado.id)
            db.session.delete(menu)
        for receta_creada in self.recetas_creadas:
            receta = Receta.query.get(receta_creada.id)
            db.session.delete(receta)
        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def crear_receta(self):
        nuevo_receta = Receta(
            nombre=self.data_factory.word(),
            duracion=self.data_factory.random_int(),
            porcion=self.data_factory.random_int(),
            preparacion=self.data_factory.text(),
            ingredientes=[],
            usuario=self.usuario_id,
        )
        db.session.add(nuevo_receta)
        db.session.commit()
        self.recetas_creadas.append(nuevo_receta)

    def test_crear_menu_semana(self):
        nombre_nuevo_menu = self.data_factory.word()
        fecha_inicial = self.data_factory.date()
        fecha_final = (
            datetime.strptime(fecha_inicial, "%Y-%m-%d") + timedelta(days=6)
        ).strftime("%Y-%m-%d")

        nuevo_menu = {
            "nombre": nombre_nuevo_menu,
            "fechaInicial": fecha_inicial,
            "fechaFinal": fecha_final,
            "recetas": [
                {"id": 1, "numero_platos": 5},
                {"id": 2, "numero_platos": 2},
                {"id": 3, "numero_platos": 7},
            ],
            "id_restaurante": 1,
        }
        endpoint_menu_semana = "/menu-semana/1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        resultado_nuevo_menu_semana = self.client.post(
            endpoint_menu_semana, data=json.dumps(nuevo_menu), headers=headers
        )
        datos_respuesta = json.loads(resultado_nuevo_menu_semana.get_data())
        menu = MenuSemana.query.get(datos_respuesta["id"])
        self.menu_semana_creados.append(menu)

        self.assertEqual(resultado_nuevo_menu_semana.status_code, 200)
        self.assertEqual(datos_respuesta["nombre"], menu.nombre)
        self.assertIsNotNone(datos_respuesta["id"])

    def test_get_menu_semana(self):
        endpoint_menu_semana = "/menu-semana/1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }
        resultado_get_menu_semana = self.client.get(
            endpoint_menu_semana, headers=headers
        )
        datos_respuesta = json.loads(resultado_get_menu_semana.get_data())
        self.assertEqual(resultado_get_menu_semana.status_code, 200)

    def test_crear_menu_semana(self):
        nombre_nuevo_menu = self.data_factory.word()
        fecha_inicial = self.data_factory.date()
        fecha_final = (
            datetime.strptime(fecha_inicial, "%Y-%m-%d") + timedelta(days=6)
        ).strftime("%Y-%m-%d")

        nuevo_menu = {
            "nombre": nombre_nuevo_menu,
            "fechaInicial": fecha_inicial,
            "fechaFinal": fecha_final,
            "recetas": [
                {"id": 1, "numero_platos": 5},
                {"id": 2, "numero_platos": 2},
                {"id": 3, "numero_platos": 7},
            ],
            "id_restaurante": 1,
        }
        endpoint_menu_semana = "/menu-semana/1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        resultado_nuevo_menu_semana = self.client.post(
            endpoint_menu_semana, data=json.dumps(nuevo_menu), headers=headers
        )
        datos_respuesta = json.loads(resultado_nuevo_menu_semana.get_data())
        menu = MenuSemana.query.get(datos_respuesta["id"])
        self.menu_semana_creados.append(menu)

        endpoint_editar_menu_semana = "/menu-semana/1/" + datos_respuesta["id"]

        nombre_editado = self.data_factory.name()
        nuevo_menu["nombre"] = nombre_editado
        resultado_nuevo_menu_semana = self.client.put(
            endpoint_editar_menu_semana, data=json.dumps(nuevo_menu), headers=headers
        )
        datos_editados_respuesta = json.loads(resultado_nuevo_menu_semana.get_data())

        menu = MenuSemana.query.get(datos_editados_respuesta["id"])

        self.assertEqual(resultado_nuevo_menu_semana.status_code, 200)
        self.assertEqual(datos_editados_respuesta["nombre"], menu.nombre)
        self.assertIsNotNone(datos_editados_respuesta["id"])
