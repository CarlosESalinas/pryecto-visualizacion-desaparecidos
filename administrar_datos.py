import os 
import logging
from pathlib import Path
import pandas as pd
import json 
import numpy as np

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Log a archivo
        logging.StreamHandler()          # Log a consola
    ]
)

class AdministrarDatos:
    def __init__(self, path=None):
        # Inicializa el logger para esta instancia
        self.logger = logging.getLogger(self.__class__.__name__)
        self.df = self.cargar_datos(path if path else self.ruta_por_defecto())
    
    def ruta_por_defecto(self):
        """Define la ruta por defecto al dataset (relativa al proyecto)"""
        return str(Path(__file__).parent / "Dataset" / "Fichas_procesado.xlsx")
    
    def cargar_datos(self, path):
        try:
            self.logger.info(f"Intentando cargar datos desde: {path}")
            df = pd.read_excel(path)
            self.logger.info("Datos cargados exitosamente")
            return self.preprocesar_datos(df)
        except FileNotFoundError as e:
            self.logger.error(f"Archivo no encontrado: {path}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error al cargar datos: {str(e)}", exc_info=True)
            raise

    def preprocesar_datos(self, df):
        columnas_categoricas = ['Estado', 'Municipio', 'Sexo', 'Género', 'Complexión', 'Tez', 'Cabello']
        for col in columnas_categoricas:
            if col in df.columns:
                df[col] = df[col].astype('category')
        return df
        
    def generar_opciones_highcharts(self):
        """Genera todas las opciones para Highcharts"""
        opciones = {
            'evolucion_temporal': self._opciones_evolucion_temporal(),
            'evolucion_temporal_municipios': self._opciones_evolucion_temporal_municipios(),
            'municipios': self._opciones_municipios(),
            'genero': self._opciones_genero(),
            'histograma': self._opciones_histograma()
        }
       # Convertir a JSON usando el parámetro default para manejar numpy types
        return json.loads(json.dumps(opciones, default=lambda x: int(x) if isinstance(x, np.integer) else float(x) if isinstance(x, np.floating) else None))
    
    def _opciones_evolucion_temporal(self):
        datos_agrupados = self.df.groupby(['Año de Desaparición', 'Sexo'], observed=False).size().reset_index(name='Count')
        
        series = []
        for genero in datos_agrupados['Sexo'].unique():
            datos_genero = datos_agrupados[datos_agrupados['Sexo'] == genero]
            series.append({
                'name': str(genero),
                'data': datos_genero[['Año de Desaparición', 'Count']].values.tolist(),
                'type': 'line',
                'marker': {'enabled': 'true'}
            })
        
        return {
            'chart': {'type': 'line'},
            'title': {'text': 'Evolución temporal de desapariciones por género'},
            'xAxis': {'title': {'text': 'Año'}, 'type': 'category'},
            'yAxis': {'title': {'text': 'Número de casos'}},
            'series': series,
            'colors': ['#0D1E40', '#177DA6', '#45A9BF'],  # Usando tu paleta de colores
            'legend': {
                'layout': 'vertical',
                'align': 'right',
                'verticalAlign': 'middle',
                'borderWidth': 0
            }
        }
    
    def _opciones_evolucion_temporal_municipios(self):
        # Obtener los 5 municipios con más casos
        top_municipios = self.df['Municipio'].value_counts().head(8).index
        
        # Filtrar el DataFrame original para solo estos municipios
        df_top = self.df[self.df['Municipio'].isin(top_municipios)].copy()  # Usamos copy() para evitar SettingWithCopyWarning
        
        # Primero agrupar por año, municipio y sexo
        datos_agrupados = df_top.groupby(['Año de Desaparición', 'Municipio', 'Sexo']).size().reset_index(name='Count')
        
        series = []
        for municipio in top_municipios:
            datos_municipio = datos_agrupados[datos_agrupados['Municipio'] == municipio]
            
            # Preparar datos para Highcharts
            data = []
            for año in datos_municipio['Año de Desaparición'].unique():
                fila = datos_municipio[datos_municipio['Año de Desaparición'] == año]
                total = fila['Count'].sum()
                hombres = fila[fila['Sexo'] == 'HOMBRE']['Count'].sum() if 'HOMBRE' in fila['Sexo'].values else 0
                mujeres = fila[fila['Sexo'] == 'MUJER']['Count'].sum() if 'MUJER' in fila['Sexo'].values else 0
                
                data.append({
                    'x': int(año),
                    'y': int(total),
                    'name': f"Hombres: {hombres}<br>Mujeres: {mujeres}"
                })

            series.append({
                'name': str(municipio),
                'data': data,
                'type': 'line',
                'marker': {'enabled': True},
                'lineWidth': 2
            })
        
        return {
            'chart': {'type': 'line'},
            'title': {'text': 'Evolución de desapariciones en los 5 municipios más afectados'},
            'xAxis': {
                'title': {'text': 'Año'},
                'crosshair': True,
                'allowDecimals': False
            },
            'yAxis': {
                'title': {'text': 'Número de casos'},
                'min': 0
            },
            'tooltip': {
            'headerFormat': '<b>{series.name}</b><br>',
            'pointFormat': 'Año: {point.x}<br>Total: {point.y}<br>{point.name}'
            },
            'series': series,
            'colors': ['#0D1E40', '#177DA6', '#45A9BF', '#2E5984', '#1E3F66'],
            'legend': {
                'layout': 'vertical',
                'align': 'right',
                'verticalAlign': 'middle',
                'borderWidth': 0
            }
        }

    def _opciones_municipios(self):
        # Obtener los 8 municipios con más casos
        top_municipios = self.df['Municipio'].value_counts().head(8).index
        
        # Filtrar el DataFrame para estos municipios
        df_top = self.df[self.df['Municipio'].isin(top_municipios)]
        
        # Calcular totales por municipio y género
        conteo_por_genero = df_top.groupby(['Municipio', 'Sexo']).size().unstack(fill_value=0)
        
        # Preparar datos para el gráfico
        datos = []
        for municipio in top_municipios:
            total = conteo_por_genero.loc[municipio].sum()
            hombres = conteo_por_genero.loc[municipio, 'HOMBRE'] if 'HOMBRE' in conteo_por_genero.columns else 0
            mujeres = conteo_por_genero.loc[municipio, 'MUJER'] if 'MUJER' in conteo_por_genero.columns else 0
            
            datos.append({
                'y': int(total),
                'municipio': str(municipio),
                'hombres': int(hombres),
                'mujeres': int(mujeres),
                'color': {
                    'linearGradient': { 'x1': 0, 'y1': 0, 'x2': 0, 'y2': 1 },
                    'stops': [
                        [0, '#b3cde0'],
                        [1, '#005b96']
                    ]
                }
            })
        
        return {
            'chart': {
                'type': 'bar',
                'height': '500px'
            },
            'title': {
                'text': 'Top 8 Municipios con más Casos Reportados'
            },
            'xAxis': {
                'categories': [d['municipio'] for d in datos],
                'title': {
                    'text': 'Municipios'
                }
            },
            'yAxis': {
                'title': {
                    'text': 'Número de Casos'
                }
            },
            'series': [{
                'name': 'Casos',
                'data': datos,
                'colorByPoint': True,
                'borderRadius': 3,
                'borderWidth': 0
            }],
            'plotOptions': {
                'bar': {
                    'dataLabels': {
                        'enabled': True,
                        'format': '{point.y}',
                        'color': "#FFFFFF",
                        'style': {
                            'textShadow': '0 0 3px #000',
                            'fontWeight': 'bold'
                        }
                    }
                }
            },
            'tooltip': {
                'headerFormat': '<b>{point.municipio}</b><br>',
                'pointFormat': '''
                    Total: <b>{point.y}</b><br>
                    Hombres: <b>{point.hombres}</b><br>
                    Mujeres: <b>{point.mujeres}</b>
                ''',
                'useHTML': True,
                'style': {
                    'color': '#333'
                }
            }
        }
        
    def _opciones_genero(self):
        conteo_genero = self.df['Genero'].value_counts()
        
        # Formatear los datos para Highcharts
        data = []
        for genero, count in conteo_genero.items():
            data.append({
                'name': genero,
                'y': int(count)  # Convertir a int para asegurar serialización
            })
        
        return {
            'chart': {'type': 'pie'},
            'title': {'text': 'Distribución por Género'},
            'plotOptions': {
                'pie': {
                    'innerSize': '50%',
                    'dataLabels': {
                        'enabled': True,
                        'format': '<b>{point.name}</b>: {point.y} ({point.percentage:.1f}%)',
                        'style': {
                            'fontWeight': 'bold',
                        }
                    }
                }
            },
            'series': [{
                'name': 'Género',
                'data': data,
                'colorByPoint': True,
                'size': '80%'  # Tamaño del gráfico
            }],
            'colors': ['#0D1E40', '#177DA6', '#45A9BF', '#2E5984', '#1E3F66'],
            'tooltip': {
                'pointFormat': '<b>{point.y}</b> ({point.percentage:.1f}%)'
            },
            'legend': {
                'align': 'right',
                'verticalAlign': 'middle',
                'layout': 'vertical'
            }
        }
        
    def _opciones_histograma(self):
        # Filtrar edades válidas (>= 0)
        edades_validas = self.df[self.df['Edad al Momento de Desaparicón'] >= 0]['Edad al Momento de Desaparicón']
        
        # Contar casos por edad y ordenar
        conteo_anual = edades_validas.value_counts().sort_index()
        
        # Calcular mediana
        mediana = edades_validas.median()
        
        # Preparar datos para Highcharts (x = edad, y = casos)
        data = [{'x': int(edad), 'y': int(casos)} for edad, casos in conteo_anual.items()]
        
        return {
            'chart': {
                'type': 'column',
                'zoomType': 'x'  # Permite hacer zoom en el eje X
            },
            'title': {'text': 'Histograma de Desapariciones por Edad'},
            'xAxis': {
                'title': {'text': 'Edad al Momento de Desaparición'},
                'type': 'linear',  
                'min': 0,          
                'plotLines': [{
                    'color': 'red',
                    'width': 2,
                    'value': int(mediana),
                    'label': {
                        'text': f'Mediana: {int(mediana)}',
                        'align': 'right',
                        'rotation': 0,
                        'x': 95,
                        'verticalAlign': 'top',
                        'layout': 'vertical',
                        'style': {'color': 'red', 'fontWeight': 'bold'}
                    }
                }]
            },
            'yAxis': {
                'title': {'text': 'Frecuencia'},
                'min': 0
            },
            'series': [{
                'name': 'Casos',
                'data': data,
                'colorByPoint': True,
                'dataLabels': {
                    'enabled': False
                }
            }],
            'colors': ['#0D1E40', '#177DA6', '#45A9BF'],
            'tooltip': {
                'pointFormat': 'Se repotan <b>{point.y}</b> casos de <b>{point.x} años</b>'
            }
        }
