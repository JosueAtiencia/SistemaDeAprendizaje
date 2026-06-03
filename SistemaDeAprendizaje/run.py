"""
Punto de Entrada de la Aplicación - LogicWeb UTA
Inicializa la factoría del servidor web y expone el servicio en el puerto 5000.
"""

import os
from app import create_app

app = create_app()
app.config["ROOT_DIR"] = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    # Iniciamos el servidor de Flask local en el puerto 5000
    print(f"[*] LogicWeb UTA iniciado en: http://localhost:5000")
    print(f"[*] Carpeta Raíz del Servidor: {app.config['ROOT_DIR']}")
    app.run(host='0.0.0.0', port=5000, debug=True)
python