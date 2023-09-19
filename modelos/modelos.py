import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


db = SQLAlchemy()


class MenuSemana(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    fecha_inicial = db.Column(db.Date)
    fecha_final = db.Column(db.Date)
    recetas = db.relationship("MenuReceta", cascade="all, delete, delete-orphan")
    id_restaurante = db.Column(db.Integer, db.ForeignKey("restaurante.id"))
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))


class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    unidad = db.Column(db.String(128))
    costo = db.Column(db.Numeric)
    calorias = db.Column(db.Numeric)
    sitio = db.Column(db.String(128))


class RecetaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Numeric)
    ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id"))
    receta = db.Column(db.Integer, db.ForeignKey("receta.id"))


class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    duracion = db.Column(db.Numeric)
    porcion = db.Column(db.Numeric)
    preparacion = db.Column(db.String)
    ingredientes = db.relationship(
        "RecetaIngrediente", cascade="all, delete, delete-orphan"
    )
    usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))


class Rol(enum.Enum):
    ADMINISTRADOR = 1
    CHEF = 2


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(128))  # correo del chef
    contrasena = db.Column(db.String(50))
    rol = db.Column(db.Enum(Rol))
    nombre = db.Column(db.String(128))
    restaurante_id = db.Column(db.Integer, db.ForeignKey("restaurante.id"))
    recetas = db.relationship("Receta", cascade="all, delete, delete-orphan")
    restaurantes = db.relationship("Restaurante", foreign_keys=[restaurante_id])
    menu_semana = db.relationship(
        "MenuSemana",
        cascade="all, delete, delete-orphan",
        foreign_keys=[MenuSemana.id_usuario],
    )


class Restaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(15))
    facebook = db.Column(db.String(500))
    twitter = db.Column(db.String(500))
    instagram = db.Column(db.String(500))
    hora_atencion = db.Column(db.String(250))
    is_en_lugar = db.Column(db.Boolean, unique=False, default=False)
    is_domicilios = db.Column(db.Boolean, unique=False, default=False)
    tipo_comida = db.Column(db.String(200))
    is_rappi = db.Column(db.Boolean, unique=False, default=False)
    is_didi = db.Column(db.Boolean, unique=False, default=False)
    administrador_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    chefs = db.relationship("Usuario", foreign_keys=[Usuario.restaurante_id])
    menu_semana = db.relationship(
        "MenuSemana",
        cascade="all, delete, delete-orphan",
        foreign_keys=[MenuSemana.id_restaurante],
    )


class MenuReceta(db.Model):
    __tablename__ = "menu_receta"
    id = db.Column(db.Integer, primary_key=True)
    menu = db.Column(db.Integer, db.ForeignKey("menu_semana.id"))
    receta = db.Column(db.Integer, db.ForeignKey("receta.id"))
    numero_platos = db.Column(db.Integer)


class RestauranteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurante
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()
    chefs = fields.List(fields.Nested("UsuarioSchema"))
    menu_semana = fields.List(fields.Nested("MenuSemanaSchema"))


class IngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ingrediente
        load_instance = True

    id = fields.String()
    costo = fields.String()
    calorias = fields.String()


class RecetaIngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RecetaIngrediente
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()
    cantidad = fields.String()
    ingrediente = fields.String()


class RecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Receta
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()
    duracion = fields.String()
    porcion = fields.String()
    ingredientes = fields.List(fields.Nested(RecetaIngredienteSchema()))


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

    id = fields.String()
    rol = fields.String()


class MenuRecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MenuReceta
        include_relationships = True
        include_fk = True
        load_instance = True
    numero_platos = fields.Integer()
    # receta = fields.String()


class MenuSemanaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MenuSemana
        include_relationships = True
        load_instance = True

    id = fields.String()
    nombre = fields.String()
    fecha_inicial = fields.Date()
    fecha_final = fields.Date()
    recetas = fields.List(fields.Nested(MenuRecetaSchema()))
    usuario = fields.Nested(UsuarioSchema())
