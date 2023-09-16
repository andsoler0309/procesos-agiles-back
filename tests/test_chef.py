import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Restaurante, Rol

from app import app


class TestChef(TestCase):
    def setUp(self):
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

        self.restaurante = Restaurante(
            nombre=self.data_factory.sentence(),
            direccion=self.data_factory.sentence(),
            telefono=self.data_factory.sentence(),
            facebook=self.data_factory.sentence(),
            twitter=self.data_factory.sentence(),
            instagram=self.data_factory.sentence(),
            hora_atencion=self.data_factory.sentence(),
            is_en_lugar=random.choice([True, False]),
            is_domicilios=random.choice([True, False]),
            tipo_comida=self.data_factory.sentence(),
            is_rappi=random.choice([True, False]),
            is_didi=random.choice([True, False]),
            administrador_id=respuesta_login["id"],
        )

        db.session.add(self.restaurante)
        db.session.commit()

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]

        self.chefs_creados = []

    def tearDown(self):
        for chef_creado in self.chefs_creados:
            chef = Usuario.query.get(chef_creado.id)
            db.session.delete(chef)
            db.session.commit()

        restaurante = Restaurante.query.get(self.restaurante.id)
        db.session.delete(restaurante)
        db.session.commit()

        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_crear_chef(self):
        # Crear los datos del chef
        nuevo_chef = {
            "nombre": self.data_factory.sentence(),
            "usuario": self.data_factory.sentence(),
            "contrasena": self.data_factory.sentence(),
            "rol": Rol.CHEF.value,
            "restaurante_id": self.restaurante.id,
        }

        resultado_nuevo_chef = self.client.post(
            f"/chef/{self.usuario_id}",
            data=json.dumps(nuevo_chef),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        datos_respuesta = json.loads(resultado_nuevo_chef.get_data())
        chef_creado = Usuario.query.get(datos_respuesta["id"])
        self.chefs_creados.append(chef_creado)

        # Se verifica los datos del chef creado
        self.assertIsNotNone(chef_creado)
        self.assertEqual(chef_creado.rol, Rol.CHEF)
        self.assertEqual(chef_creado.nombre, nuevo_chef["nombre"])
        self.assertEqual(chef_creado.usuario, nuevo_chef["usuario"])
        self.assertEqual(chef_creado.restaurante_id, nuevo_chef["restaurante_id"])

    def test_listar_chefs(self):
        for i in range(3):
            nuevo_chef = Usuario(
                nombre=self.data_factory.sentence(),
                usuario=self.data_factory.sentence(),
                contrasena=self.data_factory.sentence(),
                rol=Rol.CHEF,
                restaurante_id=self.restaurante.id,
            )
            db.session.add(nuevo_chef)
            db.session.commit()
            self.chefs_creados.append(nuevo_chef)

        solicitud_listar_chefs = self.client.get(
            f"/chefs/{self.usuario_id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        respuesta_listar_chefs = json.loads(solicitud_listar_chefs.get_data())

        self.assertEqual(solicitud_listar_chefs.status_code, 200)
        self.assertGreaterEqual(len(respuesta_listar_chefs), 3)

        for chef in respuesta_listar_chefs:
            self.assertIn("id", chef)
            self.assertIn("nombre", chef)
            self.assertIn("usuario", chef)
            self.assertIn("rol", chef)
            self.assertIn("restaurantes", chef)

    def test_detalle_chefs(self):
        nuevo_chef = Usuario(
            nombre=self.data_factory.sentence(),
            usuario=self.data_factory.sentence(),
            contrasena=self.data_factory.sentence(),
            rol=Rol.CHEF,
            restaurante_id=self.restaurante.id,
        )
        db.session.add(nuevo_chef)
        db.session.commit()
        self.chefs_creados.append(nuevo_chef)

        chef_id = Usuario.query.filter(Usuario.usuario == nuevo_chef.usuario).first().id

        solicitud_detalle_chefs = self.client.get(
            f"/chef/{self.usuario_id}/{chef_id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        chef = json.loads(solicitud_detalle_chefs.get_data())

        self.assertEqual(solicitud_detalle_chefs.status_code, 200)

        self.assertIn("id", chef)
        self.assertIn("nombre", chef)
        self.assertIn("usuario", chef)
        self.assertIn("rol", chef)
        self.assertIn("restaurantes", chef)

    def test_editar_chef(self):
        nuevo_chef = Usuario(
            nombre=self.data_factory.sentence(),
            usuario=self.data_factory.sentence(),
            contrasena=self.data_factory.sentence(),
            rol=Rol.CHEF,
            restaurante_id=self.restaurante.id,
        )
        db.session.add(nuevo_chef)
        db.session.commit()
        self.chefs_creados.append(nuevo_chef)

        chef_id = Usuario.query.filter(Usuario.usuario == nuevo_chef.usuario).first().id

        datos_chef = {
            "nombre": self.data_factory.sentence(),
            "usuario": self.data_factory.sentence(),
            "contrasena": self.data_factory.sentence(),
            "rol": Rol.CHEF.value,
            "restaurante_id": self.restaurante.id,
        }

        solicitud_editar_chef = self.client.put(
            f"/chef/{self.usuario_id}/{chef_id}",
            data=json.dumps(datos_chef),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        chef = json.loads(solicitud_editar_chef.get_data())

        self.assertEqual(solicitud_editar_chef.status_code, 200)

        self.assertIn("id", chef)
        self.assertIn("nombre", chef)
        self.assertIn("usuario", chef)
        self.assertIn("rol", chef)
        self.assertIn("restaurantes", chef)
