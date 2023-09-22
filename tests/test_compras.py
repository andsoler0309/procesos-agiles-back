import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from datetime import datetime, timedelta
from modelos import db, Usuario, MenuSemana, Receta,Ingrediente, Rol, RecetaIngrediente, Restaurante


from app import app


class TestCompras(TestCase):
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
        self.ingredientes_creados = []
        self.recetas_creadas = []
        self.menu_semana_creados = []
        self.restaurantes_creados = []
        
        self.crear_ingrediente()
        self.crear_receta()
        self.crear_restaurante()
        self.crear_menu_semana()
        

    def test_calcular_compras(self):
        endpoint_menu_semana = "/menu-compras/1/1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        resultado_get_menu_compras = self.client.get(
            endpoint_menu_semana, headers=headers
        )

        datos_respuesta = json.loads(resultado_get_menu_compras.get_data())
        self.assertEqual(resultado_get_menu_compras.status_code, 200)
        self.assertEqual(datos_respuesta["total"], '60.00')
        self.assertEqual(len(datos_respuesta["ingredientes"]), 1)
        

    def tearDown(self):
        for menu_creado in self.menu_semana_creados:
            menus = MenuSemana.query.get(menu_creado.id)
            db.session.delete(menus)
            db.session.commit()

        for restaurante in self.restaurantes_creados:
            restaurante = Restaurante.query.get(restaurante.id)
            db.session.delete(restaurante)
            db.session.commit()

        for receta_creada in self.recetas_creadas:
            receta = Receta.query.get(receta_creada.id)
            db.session.delete(receta)
            db.session.commit()
        
        for ingrediente_creado in self.ingredientes_creados:
            ingrediente = Ingrediente.query.get(ingrediente_creado.id)
            db.session.delete(ingrediente)
            db.session.commit

        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    # Crear restaurante
    def crear_restaurante(self):    
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
            "id":111,
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
        datos_respuesta = json.loads(resultado_nuevo_restaurante.get_data())
        restaurante = Restaurante.query.get(datos_respuesta["id"])
        self.restaurantes_creados.append(restaurante)

    # Crear ingrediente
    def crear_ingrediente(self):

        nombre_nuevo_ingrediente = "gomas"
        unidad_nuevo_ingrediente = self.data_factory.sentence()
        costo_nuevo_ingrediente = 1.0
        calorias_nuevo_ingrediente = round(random.uniform(0.1, 0.99), 2)
        sitio_nuevo_ingrediente = self.data_factory.sentence()

        # Crear el json con el ingrediente a crear
        nuevo_ingrediente1 = Ingrediente(
            id = 999,
            nombre = nombre_nuevo_ingrediente,
            unidad = unidad_nuevo_ingrediente,
            costo = costo_nuevo_ingrediente,
            calorias = calorias_nuevo_ingrediente,
            sitio = sitio_nuevo_ingrediente,
        )

        db.session.add(nuevo_ingrediente1)
        db.session.commit()
        self.ingredientes_creados.append(nuevo_ingrediente1)

    # Crear Receta
    def crear_receta(self):
        nueva_receta_ingrediente = RecetaIngrediente(
            cantidad = 2,
            ingrediente = int(999)
            )
        nueva_receta_ingrediente2 = RecetaIngrediente(
        cantidad = 2,
        ingrediente = int(999)
        )
        nueva_receta_ingrediente3 = RecetaIngrediente(
        cantidad = 2,
        ingrediente = int(999)
        )
        
        nueva_receta = Receta(
            id = 777,
            nombre="varias gomas",
            duracion=self.data_factory.random_int(),
            porcion=2,
            preparacion=self.data_factory.text(),
            ingredientes=[],
            usuario=self.usuario_id,
        )
        nueva_receta.ingredientes.append(nueva_receta_ingrediente)
        nueva_receta.ingredientes.append(nueva_receta_ingrediente2)
        nueva_receta.ingredientes.append(nueva_receta_ingrediente3)
        db.session.add(nueva_receta)
        db.session.commit()
        self.recetas_creadas.append(nueva_receta)

    #Crear Menu semana
    def crear_menu_semana(self):
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
                {"id": 777, "numero_platos": 10}
            ],
            "id_restaurante": 111,
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


