import json
from operator import itemgetter
from decimal import Decimal
from flask import request
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
import hashlib
from datetime import datetime
from sqlalchemy.orm import joinedload

from modelos import (
    db,
    Ingrediente,
    IngredienteSchema,
    RecetaIngrediente,
    RecetaIngredienteSchema,
    Receta,
    RecetaSchema,
    Usuario,
    UsuarioSchema,
    Restaurante,
    RestauranteSchema,
    Rol,
    MenuSemana,
    MenuSemanaSchema,
    MenuReceta,
    MenuRecetaSchema,
)

ingrediente_schema = IngredienteSchema()
receta_ingrediente_schema = RecetaIngredienteSchema()
receta_schema = RecetaSchema()
usuario_schema = UsuarioSchema()
restaurante_schema = RestauranteSchema()
menu_semana_schema = MenuSemanaSchema()
menu_receta_schema = MenuRecetaSchema()


class VistaSignIn(Resource):
    def post(self):
        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]
        ).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(
                request.json["contrasena"].encode("utf-8")
            ).hexdigest()
            nuevo_usuario = Usuario(
                usuario=request.json["usuario"],
                contrasena=contrasena_encriptada,
                rol=Rol.ADMINISTRADOR,
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
        else:
            return "El usuario ya existe", 404

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        if usuario.rol == Rol.ADMINISTRADOR:
            return "No puedes eliminar administradores", 403
        # Receta.query.filter(usuario.)
        db.session.delete(usuario)
        db.session.commit()
        return "", 204


class VistaLogIn(Resource):
    def post(self):
        contrasena_encriptada = hashlib.md5(
            request.json["contrasena"].encode("utf-8")
        ).hexdigest()
        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"],
            Usuario.contrasena == contrasena_encriptada,
        ).first()
        db.session.commit()
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {
                "mensaje": "Inicio de sesión exitoso",
                "token": token_de_acceso,
                "id": usuario.id,
                "rol": usuario.rol.name,
            }


class VistaIngredientes(Resource):
    @jwt_required()
    def get(self):
        ingredientes = Ingrediente.query.all()
        return [ingrediente_schema.dump(ingrediente) for ingrediente in ingredientes]

    @jwt_required()
    def post(self):
        nuevo_ingrediente = Ingrediente(
            nombre=request.json["nombre"],
            unidad=request.json["unidad"],
            costo=float(request.json["costo"]),
            calorias=float(request.json["calorias"]),
            sitio=request.json["sitio"],
        )

        db.session.add(nuevo_ingrediente)
        db.session.commit()
        return ingrediente_schema.dump(nuevo_ingrediente)


class VistaIngrediente(Resource):
    @jwt_required()
    def get(self, id_ingrediente):
        return ingrediente_schema.dump(Ingrediente.query.get_or_404(id_ingrediente))

    @jwt_required()
    def put(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        ingrediente.nombre = request.json["nombre"]
        ingrediente.unidad = request.json["unidad"]
        ingrediente.costo = float(request.json["costo"])
        ingrediente.calorias = float(request.json["calorias"])
        ingrediente.sitio = request.json["sitio"]
        db.session.commit()
        return ingrediente_schema.dump(ingrediente)

    @jwt_required()
    def delete(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        recetasIngrediente = RecetaIngrediente.query.filter_by(
            ingrediente=id_ingrediente
        ).all()
        if not recetasIngrediente:
            db.session.delete(ingrediente)
            db.session.commit()
            return "", 204
        else:
            return "El ingrediente se está usando en diferentes recetas", 409


class VistaRecetas(Resource):
    @jwt_required()
    def get(self, id_usuario):
        recetas = Receta.query.filter_by(usuario=str(id_usuario)).all()
        resultados = [receta_schema.dump(receta) for receta in recetas]
        ingredientes = Ingrediente.query.all()
        for receta in resultados:
            for receta_ingrediente in receta["ingredientes"]:
                self.actualizar_ingredientes_util(receta_ingrediente, ingredientes)

        return resultados

    @jwt_required()
    def post(self, id_usuario):
        nueva_receta = Receta(
            nombre=request.json["nombre"],
            preparacion=request.json["preparacion"],
            ingredientes=[],
            usuario=id_usuario,
            duracion=float(request.json["duracion"]),
            porcion=float(request.json["porcion"]),
        )
        for receta_ingrediente in request.json["ingredientes"]:
            nueva_receta_ingrediente = RecetaIngrediente(
                cantidad=receta_ingrediente["cantidad"],
                ingrediente=int(receta_ingrediente["idIngrediente"]),
            )
            nueva_receta.ingredientes.append(nueva_receta_ingrediente)

        db.session.add(nueva_receta)
        db.session.commit()
        return ingrediente_schema.dump(nueva_receta)

    def actualizar_ingredientes_util(self, receta_ingrediente, ingredientes):
        for ingrediente in ingredientes:
            if str(ingrediente.id) == receta_ingrediente["ingrediente"]:
                receta_ingrediente["ingrediente"] = ingrediente_schema.dump(ingrediente)
                receta_ingrediente["ingrediente"]["costo"] = float(
                    receta_ingrediente["ingrediente"]["costo"]
                )


class VistaReceta(Resource):
    @jwt_required()
    def get(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        ingredientes = Ingrediente.query.all()
        resultados = receta_schema.dump(Receta.query.get_or_404(id_receta))
        recetaIngredientes = resultados["ingredientes"]
        for recetaIngrediente in recetaIngredientes:
            for ingrediente in ingredientes:
                if str(ingrediente.id) == recetaIngrediente["ingrediente"]:
                    recetaIngrediente["ingrediente"] = ingrediente_schema.dump(
                        ingrediente
                    )
                    recetaIngrediente["ingrediente"]["costo"] = float(
                        recetaIngrediente["ingrediente"]["costo"]
                    )

        return resultados

    @jwt_required()
    def put(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        receta.nombre = request.json["nombre"]
        receta.preparacion = request.json["preparacion"]
        receta.duracion = float(request.json["duracion"])
        receta.porcion = float(request.json["porcion"])

        # Verificar los ingredientes que se borraron
        for receta_ingrediente in receta.ingredientes:
            borrar = self.borrar_ingrediente_util(
                request.json["ingredientes"], receta_ingrediente
            )

            if borrar == True:
                db.session.delete(receta_ingrediente)

        db.session.commit()

        for receta_ingrediente_editar in request.json["ingredientes"]:
            if receta_ingrediente_editar["id"] == "":
                # Es un nuevo ingrediente de la receta porque no tiene código
                nueva_receta_ingrediente = RecetaIngrediente(
                    cantidad=receta_ingrediente_editar["cantidad"],
                    ingrediente=int(receta_ingrediente_editar["idIngrediente"]),
                )
                receta.ingredientes.append(nueva_receta_ingrediente)
            else:
                # Se actualiza el ingrediente de la receta
                receta_ingrediente = self.actualizar_ingrediente_util(
                    receta.ingredientes, receta_ingrediente_editar
                )
                db.session.add(receta_ingrediente)

        db.session.add(receta)
        db.session.commit()
        return ingrediente_schema.dump(receta)

    @jwt_required()
    def delete(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        db.session.delete(receta)
        db.session.commit()
        return "", 204

    def borrar_ingrediente_util(self, receta_ingredientes, receta_ingrediente):
        borrar = True
        for receta_ingrediente_editar in receta_ingredientes:
            if receta_ingrediente_editar["id"] != "":
                if int(receta_ingrediente_editar["id"]) == receta_ingrediente.id:
                    borrar = False

        return borrar

    def actualizar_ingrediente_util(
        self, receta_ingredientes, receta_ingrediente_editar
    ):
        receta_ingrediente_retornar = None
        for receta_ingrediente in receta_ingredientes:
            if int(receta_ingrediente_editar["id"]) == receta_ingrediente.id:
                receta_ingrediente.cantidad = receta_ingrediente_editar["cantidad"]
                receta_ingrediente.ingrediente = receta_ingrediente_editar[
                    "idIngrediente"
                ]
                receta_ingrediente_retornar = receta_ingrediente

        return receta_ingrediente_retornar


class VistaRestaurantes(Resource):
    @jwt_required()
    def post(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        restaurante = (
            Restaurante.query.filter(Restaurante.administrador_id == id_usuario)
            .filter(Restaurante.nombre == request.json["nombre"])
            .first()
        )

        if usuario is None:
            return "El Administrador no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden crear Restaurantes", 401
        elif restaurante is not None:
            return (
                "Ya existe un restaurante con nombre: "
                + request.json["nombre"]
                + str(restaurante),
                422,
            )

        else:
            nuevo_restaurante = Restaurante(
                nombre=request.json["nombre"],
                direccion=request.json["direccion"],
                telefono=request.json["telefono"],
                hora_atencion=request.json["hora_atencion"],
                facebook=request.json["facebook"],
                instagram=request.json["instagram"],
                twitter=request.json["twitter"],
                tipo_comida=request.json["tipo_comida"],
                is_en_lugar=request.json["is_en_lugar"],
                is_rappi=request.json["is_rappi"],
                is_didi=request.json["is_didi"],
                is_domicilios=request.json["is_domicilios"],
                administrador_id=id_usuario,
            )

        db.session.add(nuevo_restaurante)
        db.session.commit()
        # TODO enviar el Schema como respuesta
        return {
            "mensaje": "Restaurante creado exitosamente",
            "id": nuevo_restaurante.id,
        }

    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El usuario no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden ver Restaurantes", 401

        restaurantes = (
            Restaurante.query.filter_by(administrador_id=id_usuario)
            .order_by(Restaurante.nombre)
            .all()
        )

        return [restaurante_schema.dump(restaurante) for restaurante in restaurantes]


class VistaDetalleRestaurante(Resource):
    @jwt_required()
    def get(self, id_usuario, id_restaurante):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()

        if usuario is None:
            return "El Administrador no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden ver el detalle del Restaurante", 401

        restaurante = Restaurante.query.filter(Restaurante.id == id_restaurante).first()
        return restaurante_schema.dump(restaurante)

    @jwt_required()
    def put(self, id_usuario, id_restaurante):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El Administrador no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden editar el Restaurante", 401

        restaurante = Restaurante.query.get_or_404(id_restaurante)
        restaurante.nombre = request.json["nombre"]
        restaurante.direccion = request.json["direccion"]
        restaurante.telefono = request.json["telefono"]
        restaurante.hora_atencion = request.json["hora_atencion"]
        restaurante.facebook = request.json["facebook"]
        restaurante.instagram = request.json["instagram"]
        restaurante.twitter = request.json["twitter"]
        restaurante.tipo_comida = request.json["tipo_comida"]
        restaurante.is_en_lugar = request.json["is_en_lugar"]
        restaurante.is_domicilios = request.json["is_domicilios"]
        restaurante.is_rappi = request.json["is_rappi"]
        restaurante.is_didi = request.json["is_didi"]
        db.session.commit()
        return restaurante_schema.dump(restaurante)

    @jwt_required()
    def delete(self, id_usuario, id_restaurante):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El Administrador no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden eliminar el Restaurante", 401

        restaurante = Restaurante.query.get_or_404(id_restaurante)
        db.session.delete(restaurante)
        db.session.commit()
        return "", 204


class VistaMenuSemana(Resource):
    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El usuario no existe", 404
        if usuario.rol is Rol.CHEF:
            menus = MenuSemana.query.filter_by(
                id_restaurante=usuario.restaurante_id
            ).all()
        else:
            lista_restaurantes_id = [
                restaurante.id
                for restaurante in Restaurante.query.filter_by(
                    administrador_id=id_usuario
                ).all()
            ]
            menus = MenuSemana.query.filter(
                MenuSemana.id_restaurante.in_(lista_restaurantes_id)
            ).all()
        result = []
        for menu in menus:
            usuario = Usuario.query.filter_by(id=menu.id_usuario).first()
            menu_final = menu_semana_schema.dump(menu)
            menu_final["usuario"] = UsuarioSchema(only=["usuario", "rol"]).dump(usuario)
            menu_final["usuario"]["rol"] = usuario.rol.name

            recetas = []
            for menu_receta in menu.recetas:
                numero_platos = menu_receta.numero_platos
                receta = Receta.query.filter(Receta.id == menu_receta.id).first()

                receta_temp = {
                    "receta": receta_schema.dump(receta),
                    "numero_platos": numero_platos,
                }
                recetas.append(receta_temp)

            menu_final["recetas"] = recetas
            result.append(menu_final)

        return result, 200

    @jwt_required()
    def post(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        id_restaurante = None
        if usuario is None:
            return "El usuario no existe", 404
        if usuario.rol is Rol.CHEF:
            id_restaurante = usuario.restaurante_id
        else:
            id_restaurante = request.json["id_restaurante"]
        nombre_menu_repetido = MenuSemana.query.filter_by(
            nombre=request.json["nombre"]
        ).first()

        if nombre_menu_repetido is not None:
            return "El nombre del menu ya existe", 400
        try:
            fecha_inicial = datetime.strptime(
                request.json["fechaInicial"], "%Y-%m-%d"
            ).date()
            fecha_final = datetime.strptime(
                request.json["fechaFinal"], "%Y-%m-%d"
            ).date()
        except Exception as e:
            return str(e), 400

        diff_fecha = fecha_final - fecha_inicial
        if diff_fecha.days != 6:
            return "Las fechas no tienen la diferencia correcta", 400

        todos_menus = MenuSemana.query.filter_by(id_restaurante=id_restaurante).all()
        for menuTemp in todos_menus:
            if (fecha_final >= menuTemp.fecha_final >= fecha_inicial) or (
                fecha_final >= menuTemp.fecha_inicial >= fecha_inicial
            ):
                return "Las fechas tienen conflicto con las de otro menu", 400

        nuevo_menu_semana = MenuSemana(
            nombre=request.json["nombre"],
            fecha_inicial=fecha_inicial,
            fecha_final=fecha_final,
            id_restaurante=id_restaurante,
            id_usuario=id_usuario,
        )
        for receta in request.json["recetas"]:
            receta_menu = MenuReceta(
                menu=nuevo_menu_semana.id,
                receta=receta["id"],
                numero_platos=receta["numero_platos"],
            )
            nuevo_menu_semana.recetas.append(receta_menu)
        db.session.add(nuevo_menu_semana)
        db.session.commit()
        return menu_semana_schema.dump(nuevo_menu_semana), 200


class VistaEditarMenuSemana(Resource):
    @jwt_required()
    def put(self, id_usuario, id_menu):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        id_restaurante = None
        if usuario is None:
            return "El usuario no existe", 404
        if usuario.rol is Rol.CHEF:
            id_restaurante = usuario.restaurante_id
        else:
            id_restaurante = request.json["id_restaurante"]

        print("++++++")
        print(id_menu)
        menu = MenuSemana.query.filter(MenuSemana.id == id_menu).first()
        print(menu)
        print(menu_semana_schema.dump(menu))
        if menu is None:
            return "El menu no existe", 404

        try:
            fecha_inicial = datetime.strptime(
                request.json["fechaInicial"], "%Y-%m-%d"
            ).date()
            fecha_final = datetime.strptime(
                request.json["fechaFinal"], "%Y-%m-%d"
            ).date()
        except Exception as e:
            return str(e), 400

        diff_fecha = fecha_final - fecha_inicial
        if diff_fecha.days != 6:
            return "Las fechas no tienen la diferencia correcta", 400

        todos_menus = (
            MenuSemana.query.filter_by(id_restaurante=id_restaurante)
            .filter(MenuSemana.id != id_menu)
            .all()
        )
        for menuTemp in todos_menus:
            if (fecha_final >= menuTemp.fecha_final >= fecha_inicial) or (
                fecha_final >= menuTemp.fecha_inicial >= fecha_inicial
            ):
                return "Las fechas tienen conflicto con las de otro menu", 400

        menu.nombre = request.json["nombre"]
        menu.fecha_inicial = fecha_inicial
        menu.fecha_final = fecha_final
        menu.id_restaurante = id_restaurante
        menu.id_usuario = id_usuario

        menu.recetas.clear()
        for receta_id in request.json["recetas"]:
            receta_menu = MenuReceta(menu=menu.id, receta=receta_id["id"])
            menu.recetas.append(receta_menu)
        # db.session.add(menu)
        db.session.commit()
        return menu_semana_schema.dump(menu), 200

class VistaCompras(Resource):
    #@jwt_required()
    def get(self, id_usuario, id_menu):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El usuario no existe", 404

        #menu de la semana
        menu_semana = MenuSemana.query.filter(
            MenuSemana.id == id_menu
        ).first()

        
        result = []
        resultado = {
                "ingredientes":[],
                "total":""
            }
        
        for receta in menu_semana.recetas:

            total = 0

            row = {
            'nombre_ingrediente':"",
            'cantidad':"",
            'costo':"",
            "porciones":"",
            'id_ingrediente':"",
            'sitio_compra':"",
            'receta_aparece' :[]
                   }
            
            #receta
            receta_temp1 = Receta.query.filter(Receta.id == receta.receta).first()
            print(str(receta))
            for element in receta_temp1.ingredientes:
                #ingrediente
                ingrediente = Ingrediente.query.filter(Ingrediente.id == element.ingrediente).first()
                
                row.update({'nombre_ingrediente':ingrediente.nombre})
                row.update({'id_ingrediente':ingrediente.id})
                row.update({'cantidad':f"{element.cantidad:.2f}"})
                row.update({'costo':f"{ingrediente.costo:.2f}"})
                row.update({'sitio_compra':ingrediente.sitio})
                row.update({'receta_aparece':[receta_temp1.nombre]})
                
                if not any(key['id_ingrediente'] == ingrediente.id for key in result):
                    result.append(row.copy())
                else:
                    d = next(item for item in result if item['id_ingrediente'] == ingrediente.id)
                    cantidad = float(d['cantidad']) + 1
                    d['cantidad'] = f"{cantidad:.2f}"
                    costo = float(d['costo']) + 1
                    d['costo'] = f"{costo:.2f}"
                    d['sitio-compra'] = ingrediente.sitio 
                    if not any(receta_temp1.nombre in s for s in d['receta_aparece']):
                        d['receta_aparece'].append(receta_temp1.nombre)

        #ordenamiento 
        sorted_result = sorted(result, key=itemgetter('sitio_compra', 'nombre_ingrediente'))

        return sorted_result, 200


class VistaChef(Resource):
    @jwt_required()
    def post(self, id_usuario):
        administrador = Usuario.query.filter(Usuario.id == id_usuario).first()

        if administrador is None:
            return "El Administrador no existe", 404
        elif administrador.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden crear Chef", 401

        restaurante_id = request.json["restaurante_id"]

        restaurantes = Restaurante.query.filter(
            Restaurante.administrador_id == id_usuario
        ).all()

        if not any(restaurante.id == restaurante_id for restaurante in restaurantes):
            return "El restaurante no pertenece al administrador"

        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]
        ).first()

        if usuario is None:
            contrasena_encriptada = hashlib.md5(
                request.json["contrasena"].encode("utf-8")
            ).hexdigest()
            nuevo_usuario = Usuario(
                usuario=request.json["usuario"],
                contrasena=contrasena_encriptada,
                rol=Rol.CHEF,
                nombre=request.json["nombre"],
                restaurante_id=request.json["restaurante_id"],
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"mensaje": "chef creado exitosamente", "id": nuevo_usuario.id}
        else:
            return "El usuario ya existe", 404


class VistaDetalleChef(Resource):
    @jwt_required()
    def get(self, id_usuario, id_chef):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El Administrador no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden ver el detalle del Chef", 401

        chef = Usuario.query.filter(Usuario.id == id_chef).first()

        resultado = usuario_schema.dump(chef)
        restaurante = Restaurante.query.filter_by(id=resultado["restaurantes"]).first()
        resultado["restaurante"] = restaurante_schema.dump(restaurante)

        return resultado

    def put(self, id_usuario, id_chef):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El Administrador no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden ver el detalle del Chef", 401

        chef = Usuario.query.filter(Usuario.id == id_chef).first()
        chef.nombre = request.json["nombre"]
        chef.usuario = request.json["usuario"]
        chef.restaurante_id = request.json["restaurante_id"]
        db.session.commit()
        return usuario_schema.dump(chef)

    def delete(self, id_usuario, id_chef):
        administrador = Usuario.query.filter(Usuario.id == id_usuario).first()
        if administrador is None:
            return "El Administrador no existe", 404
        elif administrador.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden ver el detalle del Chef", 401

        chef = Usuario.query.filter(Usuario.id == id_chef).first()
        print(chef.recetas)
        print(chef.menu_semana)
        for receta in chef.recetas:
            receta.usuario = id_usuario

        for menu_semana in chef.menu_semana:
            menu_semana.id_usuario = id_usuario

        db.session.commit()

        db.session.delete(chef)
        db.session.commit()
        return "", 204


class VistaChefs(Resource):
    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.filter(Usuario.id == id_usuario).first()
        if usuario is None:
            return "El usuario no existe", 404
        elif usuario.rol != Rol.ADMINISTRADOR:
            return "Solo los Administradores pueden ver Chefs", 401

        restaurantes_usuario = Restaurante.query.filter_by(
            administrador_id=id_usuario
        ).all()

        chefs = (
            Usuario.query.filter(
                Usuario.restaurante_id.in_(
                    [restaurante.id for restaurante in restaurantes_usuario]
                ),
                Usuario.rol == Rol.CHEF,
            )
            .order_by(Usuario.nombre)
            .all()
        )

        resultados = [usuario_schema.dump(chef) for chef in chefs]

        for chef in resultados:
            restaurante = Restaurante.query.filter_by(id=chef["restaurantes"]).first()
            chef["restaurante"] = restaurante_schema.dump(restaurante)

        return resultados
    

