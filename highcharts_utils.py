from markupsafe import Markup

def generar_grafico(opciones, contenedor_id):
    """Genera el código HTML/JS para un gráfico Highcharts"""
    return Markup(f"""
    <div id="{contenedor_id}" class="highcharts-container"></div>
    <script>
    Highcharts.chart('{contenedor_id}', {opciones});
    </script>
    """)