import os
import logging
import datetime
from diccionario import inputs
from flask import Flask, render_template
from administrar_datos import AdministrarDatos

# Configurar logging (si no usas el archivo de configuración)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app_flask = Flask(__name__)

@app_flask.route('/')
def inicio():
    logger.info("Solicitud recibida para la página de inicio")
    try:
        datos_manager = AdministrarDatos()
        opciones = datos_manager.generar_opciones_highcharts()
        logger.info("Gráficos generados exitosamente")
        
        return render_template(
            'index.html',
            diccionario=inputs,
            año_actual=datetime.datetime.now().year,
            grafico_evolucion=opciones['evolucion_temporal'],
            grafico_evolucion_municipio=opciones['evolucion_temporal_municipios'],
            grafico_municipios=opciones['municipios'],
            grafico_genero=opciones['genero'],
            grafico_histograma=opciones['histograma']
        )
    except Exception as e:
        logger.error("Error al procesar solicitud de inicio", exc_info=True)
        raise  # O maneja el error adecuadamente para el usuario

if __name__ == '__main__':
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))