"""
Modelos ORM de SQLAlchemy - LogicWeb UTA
Define el esquema relacional mapeado a la base de datos SQLite.
Proporciona métodos bidireccionales de traducción entre los modelos ORM e Infraestructura y las Entidades del Dominio.
"""

import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app.domain.entities import Usuario, Ejercicio, Intento

# Instancia global de db que será inicializada en la app de Flask
db = SQLAlchemy()

class UserModel(db.Model):
    """Modelo ORM para la tabla de Usuarios en SQLite."""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_domain(self) -> Usuario:
        """Mapea el modelo de infraestructura a la entidad pura de Dominio."""
        return Usuario(
            id=self.id,
            username=self.username,
            email=self.email,
            password_hash=self.password_hash,
            fecha_registro=self.fecha_registro
        )

    @classmethod
    def from_domain(cls, user: Usuario) -> 'UserModel':
        """Crea una instancia ORM a partir de una entidad del dominio."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            fecha_registro=user.fecha_registro
        )


class ExerciseModel(db.Model):
    """Modelo ORM para almacenar la configuración de Ejercicios en SQLite."""
    __tablename__ = 'ejercicios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unidad_id = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion_caso_real = db.Column(db.Text, nullable=False)
    pseudocodigo = db.Column(db.Text, nullable=False)
    codigo_fuente_cpp = db.Column(db.Text, nullable=True) # Código real C++ para mostrar al estudiante
    diagrama_ruta = db.Column(db.String(255), nullable=False)
    ruta_binario_cpp = db.Column(db.String(255), nullable=False)

    def to_domain(self) -> Ejercicio:
        """Mapea el modelo de infraestructura a la entidad pura de Dominio."""
        return Ejercicio(
            id=self.id,
            unidad_id=self.unidad_id,
            titulo=self.titulo,
            descripcion_caso_real=self.descripcion_caso_real,
            pseudocodigo=self.pseudocodigo,
            diagrama_ruta=self.diagrama_ruta,
            ruta_binario_cpp=self.ruta_binario_cpp,
            codigo_fuente_cpp=self.codigo_fuente_cpp
        )

    @classmethod
    def from_domain(cls, exercise: Ejercicio) -> 'ExerciseModel':
        """Crea una instancia ORM a partir de una entidad del dominio."""
        return cls(
            id=exercise.id,
            unidad_id=exercise.unidad_id,
            titulo=exercise.titulo,
            descripcion_caso_real=exercise.descripcion_caso_real,
            pseudocodigo=exercise.pseudocodigo,
            diagrama_ruta=exercise.diagrama_ruta,
            ruta_binario_cpp=exercise.ruta_binario_cpp,
            codigo_fuente_cpp=exercise.codigo_fuente_cpp
        )


class AttemptModel(db.Model):
    """Modelo ORM para registrar en SQLite los Intentos del Juez Online."""
    __tablename__ = 'intentos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ejercicio_id = db.Column(db.Integer, db.ForeignKey('ejercicios.id'), nullable=False)
    datos_ingresados_json = db.Column(db.Text, nullable=False)  # Diccionario serializado a texto JSON
    resultado_obtenido = db.Column(db.Text, nullable=False)
    estado_oj = db.Column(db.String(10), nullable=False)  # AC, WA, RE, TLE
    fecha_intento = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones relacionales
    usuario = db.relationship('UserModel', backref=db.backref('intentos', lazy=True))
    ejercicio = db.relationship('ExerciseModel', backref=db.backref('intentos', lazy=True))

    def to_domain(self) -> Intento:
        """Mapea el modelo de infraestructura a la entidad pura de Dominio."""
        try:
            inputs = json.loads(self.datos_ingresados_json)
        except Exception:
            inputs = {}
            
        return Intento(
            id=self.id,
            usuario_id=self.usuario_id,
            ejercicio_id=self.ejercicio_id,
            datos_ingresados=inputs,
            resultado_obtenido=self.resultado_obtenido,
            estado_oj=self.estado_oj,
            fecha_intento=self.fecha_intento
        )

    @classmethod
    def from_domain(cls, attempt: Intento) -> 'AttemptModel':
        """Crea una instancia ORM a partir de una entidad del dominio."""
        return cls(
            id=attempt.id,
            usuario_id=attempt.usuario_id,
            ejercicio_id=attempt.ejercicio_id,
            datos_ingresados_json=json.dumps(attempt.datos_ingresados),
            resultado_obtenido=attempt.resultado_obtenido,
            estado_oj=attempt.estado_oj,
            fecha_intento=attempt.fecha_intento
        )
