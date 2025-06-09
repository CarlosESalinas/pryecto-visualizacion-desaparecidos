import datetime
from administrar_datos import AdministrarDatos
from highcharts_utils import generar_grafico

def crear_layout():
    datos_manager = AdministrarDatos()
    opciones = datos_manager.generar_opciones_highcharts()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Desaparecidos</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://code.highcharts.com/modules/exporting.js"></script>
        <style>
            .highcharts-container {{
                height: 500px;
                margin-bottom: 30px;
            }}
            .card {{
                margin-bottom: 30px;
            }}
        </style>
    </head>
    <body style="background-color: #F8F9FA; padding: 20px;">
        <div class="container">
            <div class="row">
                <div class="col-md-12 text-center">
                    <h1 style="color: #0E1126; font-family: 'Righteous', cursive;">
                        Análisis de Personas Desaparecidas en México
                    </h1>
                    <p style="color: #144673;">
                        Visualización interactiva de casos reportados
                    </p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    {generar_grafico(opciones['evolucion_temporal'], 'grafico-evolucion')}
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    {generar_grafico(opciones['evolucion_temporal_municipios'], 'grafico-evolucion-municipios')}
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    {generar_grafico(opciones['municipios'], 'grafico-municipios')}
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    {generar_grafico(opciones['genero'], 'grafico-genero')}
                </div>
            </div>
            
            
            <div class="row">
                <div class="col-md-12">
                    {generar_grafico(opciones['histograma'], 'grafico-histograma')}
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12 text-center">
                    <small style="color: #6c757d;">
                        Última actualización: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")} | 
                        Fuente: Registro Nacional de Personas Desaparecidas
                    </small>
                </div>
            </div>
        </div>
    </body>
    </html>
    """