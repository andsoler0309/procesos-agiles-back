import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Restaurante, Rol

from app import app


class TestRestaurante(TestCase):
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

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]

        self.restaurantes_creados = []

    def tearDown(self):
        for restaurante_creado in self.restaurantes_creados:
            restaurante = Restaurante.query.get(restaurante_creado.id)
            db.session.delete(restaurante)
            db.session.commit()

        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_crear_restaurante(self):
        # Crear los datos del restaurante
        nombre_nuevo_restaurante = self.data_factory.sentence()
        direccion_nuevo_restaurante = self.data_factory.sentence()
        telefono_nuevo_restaurante = self.data_factory.sentence()
        facebook_nuevo_restaurante = self.data_factory.sentence()
        twitter_nuevo_restaurante = self.data_factory.sentence()
        instagram_nuevo_restaurante = self.data_factory.sentence()
        hora_atencion_nuevo_restaurante = self.data_factory.sentence()
        is_en_lugar_nuevo_restaurante = random.choice([True, False])
        is_domicilios_nuevo_restaurante = random.choice([True, False])
        tipo_comida_nuevo_restaurante = self.data_factory.sentence()
        is_rappi_nuevo_restaurante = random.choice([True, False])
        is_didi_nuevo_restaurante = random.choice([True, False])
        # administrador_nuevo_restaurante = self.usuario_id

        # Crear el json con el restaurante a crear
        nuevo_restaurante = {
            "nombre": nombre_nuevo_restaurante,
            "direccion": direccion_nuevo_restaurante,
            "telefono": telefono_nuevo_restaurante,
            "facebook": facebook_nuevo_restaurante,
            "twitter": twitter_nuevo_restaurante,
            "instagram": instagram_nuevo_restaurante,
            "hora_atencion": hora_atencion_nuevo_restaurante,
            "is_en_lugar": is_en_lugar_nuevo_restaurante,
            "is_domicilios": is_domicilios_nuevo_restaurante,
            "tipo_comida": tipo_comida_nuevo_restaurante,
            "is_rappi": is_rappi_nuevo_restaurante,
            "is_didi": is_didi_nuevo_restaurante,
        }

        # Definir endpoint, encabezados y hacer el llamado
        endpoint_restaurante = f"/restaurantes/{self.usuario_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        resultado_nuevo_restaurante = self.client.post(
            endpoint_restaurante, data=json.dumps(nuevo_restaurante), headers=headers
        )

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_restaurante.get_data())
        restaurante = Restaurante.query.get(datos_respuesta["id"])
        self.restaurantes_creados.append(restaurante)

        # Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nuevo_restaurante.status_code, 200)
        self.assertEqual(datos_respuesta["mensaje"], "Restaurante creado exitosamente")
        self.assertIsNotNone(datos_respuesta["id"])

    def test_listar_restaurantes(self):
        """
        Prueba que se puedan listar los restaurantes
        """
        # genera 10 restaurantes con datos aleatorios
        for i in range(10):
            restaurante = Restaurante(
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
                administrador_id=self.usuario_id,
            )

            db.session.add(restaurante)
            db.session.commit()
            self.restaurantes_creados.append(restaurante)

        endpoint_restaurante = f"/restaurantes/{self.usuario_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        resultado_listar_restaurantes = self.client.get(
            endpoint_restaurante, headers=headers
        )

        datos_respuesta = json.loads(resultado_listar_restaurantes.get_data())
        self.assertEqual(resultado_listar_restaurantes.status_code, 200)
        self.assertEqual(len(datos_respuesta), 10)

    def test_detalle_restaurante(self):
        # Crear los datos del restaurante
        nombre_nuevo_restaurante = self.data_factory.sentence()
        direccion_nuevo_restaurante = self.data_factory.sentence()
        telefono_nuevo_restaurante = self.data_factory.sentence()
        facebook_nuevo_restaurante = self.data_factory.sentence()
        twitter_nuevo_restaurante = self.data_factory.sentence()
        instagram_nuevo_restaurante = self.data_factory.sentence()
        hora_atencion_nuevo_restaurante = self.data_factory.sentence()
        is_en_lugar_nuevo_restaurante = random.choice([True, False])
        is_domicilios_nuevo_restaurante = random.choice([True, False])
        tipo_comida_nuevo_restaurante = self.data_factory.sentence()
        is_rappi_nuevo_restaurante = random.choice([True, False])
        is_didi_nuevo_restaurante = random.choice([True, False])

        # Crear el json con el restaurante a crear
        nuevo_restaurante = {
            "nombre": nombre_nuevo_restaurante,
            "direccion": direccion_nuevo_restaurante,
            "telefono": telefono_nuevo_restaurante,
            "facebook": facebook_nuevo_restaurante,
            "twitter": twitter_nuevo_restaurante,
            "instagram": instagram_nuevo_restaurante,
            "hora_atencion": hora_atencion_nuevo_restaurante,
            "is_en_lugar": is_en_lugar_nuevo_restaurante,
            "is_domicilios": is_domicilios_nuevo_restaurante,
            "tipo_comida": tipo_comida_nuevo_restaurante,
            "is_rappi": is_rappi_nuevo_restaurante,
            "is_didi": is_didi_nuevo_restaurante,
        }

        # Definir endpoint, encabezados y hacer el llamado
        endpoint_restaurante = f"/restaurantes/{self.usuario_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        resultado_nuevo_restaurante = self.client.post(
            endpoint_restaurante, data=json.dumps(nuevo_restaurante), headers=headers
        )

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_restaurante.get_data())
        restaurante = Restaurante.query.get(datos_respuesta["id"])
        self.restaurantes_creados.append(restaurante)

        restaurante_id = (
            Restaurante.query.filter(Restaurante.nombre == nombre_nuevo_restaurante)
            .filter(Restaurante.administrador_id == self.usuario_id)
            .first()
            .id
        )

        solicitud_detalle_restaurante = self.client.get(
            f"/restaurantes/{self.usuario_id}/{restaurante_id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )

        restaurante = json.loads(solicitud_detalle_restaurante.get_data())

        self.assertEqual(solicitud_detalle_restaurante.status_code, 200)

        self.assertIn("id", restaurante)
        self.assertIn("nombre", restaurante)
        self.assertIn("telefono", restaurante)
        self.assertIn("direccion", restaurante)
        self.assertIn("hora_atencion", restaurante)
        self.assertIn("menu_semana", restaurante)

    def test_editar_restaurante(self):
        restaurante = Restaurante(
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
            administrador_id=self.usuario_id,
        )

        db.session.add(restaurante)
        db.session.commit()
        self.restaurantes_creados.append(restaurante)

        restaurante_id = (
            Restaurante.query.filter(Restaurante.nombre == restaurante.nombre)
            .filter(Restaurante.administrador_id == self.usuario_id)
            .first()
            .id
        )

        datos_restaurante = {
            "nombre": self.data_factory.sentence(),
            "direccion": self.data_factory.sentence(),
            "telefono": self.data_factory.sentence(),
            "facebook": self.data_factory.sentence(),
            "twitter": self.data_factory.sentence(),
            "instagram": self.data_factory.sentence(),
            "hora_atencion": self.data_factory.sentence(),
            "is_en_lugar": random.choice([True, False]),
            "is_domicilios": random.choice([True, False]),
            "tipo_comida": self.data_factory.sentence(),
            "is_rappi": random.choice([True, False]),
            "is_didi": random.choice([True, False]),
        }

        endpoint_restaurante = f"/restaurantes/{self.usuario_id}/{restaurante_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        resultado_editar_restaurante = self.client.put(
            endpoint_restaurante, data=json.dumps(datos_restaurante), headers=headers
        )

        datos_respuesta = json.loads(resultado_editar_restaurante.get_data())
        restaurante = Restaurante.query.get(datos_respuesta["id"])

        self.assertEqual(resultado_editar_restaurante.status_code, 200)
        self.assertEqual(restaurante.nombre, datos_restaurante["nombre"])
        self.assertEqual(restaurante.direccion, datos_restaurante["direccion"])
        self.assertEqual(restaurante.telefono, datos_restaurante["telefono"])

    def test_eliminar_restaurante(self):
        restaurante = Restaurante(
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
            administrador_id=self.usuario_id,
        )

        db.session.add(restaurante)
        db.session.commit()
        self.restaurantes_creados.append(restaurante)

        restaurante_id = (
            Restaurante.query.filter(Restaurante.nombre == restaurante.nombre)
            .filter(Restaurante.administrador_id == self.usuario_id)
            .first()
            .id
        )

        endpoint_restaurante = f"/restaurantes/{self.usuario_id}/{restaurante_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        resultado_eliminar_restaurante = self.client.delete(
            endpoint_restaurante, headers=headers
        )

        self.restaurantes_creados.pop()
        self.assertEqual(resultado_eliminar_restaurante.status_code, 204)
