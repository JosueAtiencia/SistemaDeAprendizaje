"""
Configuración General del Entorno - LogicWeb UTA
Establece las credenciales del sistema, almacenamiento de SQLite y directorios de C++.
"""

import os

class Config:
    # Directorio raíz del proyecto
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Seguridad básica para cookies y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY', 'logicweb-uta-ultra-secure-key-2026')
    
    # Ubicación de la Base de Datos SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(ROOT_DIR, 'logicweb_uta.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Entorno
    DEBUG = True
