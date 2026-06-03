"""
Implementaciones de Repositorio en SQLite - LogicWeb UTA
Adapta los contratos abstractos del dominio a SQLAlchemy y la persistencia SQLite.
"""

from typing import List, Optional
from app.domain.entities import Usuario, Ejercicio, Intento
from app.application.interfaces.repositories import UsuarioRepository, EjercicioRepository, IntentoRepository
from app.infrastructure.database.models import db, UserModel, ExerciseModel, AttemptModel

class SqliteUsuarioRepository(UsuarioRepository):
    
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        model = UserModel.query.get(usuario_id)
        return model.to_domain() if model else None

    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        model = UserModel.query.filter_by(username=username).first()
        return model.to_domain() if model else None

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        model = UserModel.query.filter_by(email=email).first()
        return model.to_domain() if model else None

    def guardar(self, usuario: Usuario) -> Usuario:
        if usuario.id is not None:
            # Actualización
            model = UserModel.query.get(usuario.id)
            if model:
                model.username = usuario.username
                model.email = usuario.email
                model.password_hash = usuario.password_hash
        else:
            # Creación
            model = UserModel.from_domain(usuario)
            db.session.add(model)
            
        db.session.commit()
        return model.to_domain()


class SqliteEjercicioRepository(EjercicioRepository):
    
    def obtener_por_id(self, ejercicio_id: int) -> Optional[Ejercicio]:
        model = ExerciseModel.query.get(ejercicio_id)
        return model.to_domain() if model else None

    def obtener_todos(self) -> List[Ejercicio]:
        models = ExerciseModel.query.all()
        return [m.to_domain() for m in models]

    def guardar(self, ejercicio: Ejercicio) -> Ejercicio:
        if ejercicio.id is not None:
            model = ExerciseModel.query.get(ejercicio.id)
            if model:
                model.unidad_id = ejercicio.unidad_id
                model.titulo = ejercicio.titulo
                model.descripcion_caso_real = ejercicio.descripcion_caso_real
                model.pseudocodigo = ejercicio.pseudocodigo
                model.diagrama_ruta = ejercicio.diagrama_ruta
                model.ruta_binario_cpp = ejercicio.ruta_binario_cpp
        else:
            model = ExerciseModel.from_domain(ejercicio)
            db.session.add(model)
            
        db.session.commit()
        return model.to_domain()


class SqliteIntentoRepository(IntentoRepository):
    
    def obtener_por_id(self, intento_id: int) -> Optional[Intento]:
        model = AttemptModel.query.get(intento_id)
        return model.to_domain() if model else None

    def obtener_por_usuario(self, usuario_id: int) -> List[Intento]:
        models = AttemptModel.query.filter_by(usuario_id=usuario_id)\
                                   .order_by(AttemptModel.fecha_intento.desc())\
                                   .all()
        return [m.to_domain() for m in models]

    def obtener_por_usuario_y_ejercicio(self, usuario_id: int, ejercicio_id: int) -> List[Intento]:
        models = AttemptModel.query.filter_by(usuario_id=usuario_id, ejercicio_id=ejercicio_id)\
                                   .order_by(AttemptModel.fecha_intento.desc())\
                                   .all()
        return [m.to_domain() for m in models]

    def obtener_estadisticas_usuario(self, usuario_id: int) -> dict:
        # Se orquesta directamente a nivel del caso de uso por flexibilidad,
        # pero exponemos los datos agregados básicos si se requiere
        models = AttemptModel.query.filter_by(usuario_id=usuario_id).all()
        intentos = [m.to_domain() for m in models]
        return {
            "total": len(intentos),
            "ac_exitos": sum(1 for i in intentos if i.estado_oj == "AC")
        }

    def guardar(self, intento: Intento) -> Intento:
        model = AttemptModel.from_domain(intento)
        db.session.add(model)
        db.session.commit()
        # Asignar la ID autogenerada de vuelta a la entidad
        intento.id = model.id
        return model.to_domain()
