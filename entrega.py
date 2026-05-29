#1
import pandas as pd
from google.colab import files
#2
print("Sube el archivo de texto con los registros de 70 caracteres:")
archivo_txt = files.upload()
nombre_txt = list(archivo_txt.keys())[0]

print("\nSube el archivo Excel con el cuadro de emergencia económica:")
archivo_excel = files.upload()
nombre_excel = list(archivo_excel.keys())[0]
#3
lineas = archivo_txt[nombre_txt].decode('utf-8').splitlines()
lineas = [l for l in lineas if len(l.strip()) > 0]

registros = []
for l in lineas:
    registros.append({
        'Linea_Original': l,
        'Motivo':                    l[0:4],
        'Tipo_Movimiento':           l[4:5],   # 0=Débito, 1=Crédito
        'Aplica_Emergencia_Economica': l[16:17],
        'Val_Inactividad':           l[55:56],
    })

df_registros = pd.DataFrame(registros)

# Etiqueta legible para Tipo Movimiento
df_registros['Tipo_Movimiento_Desc'] = df_registros['Tipo_Movimiento'].map(
    {'0': 'Débito', '1': 'Crédito'}
).fillna('Desconocido')

print(f"✅ {len(df_registros)} registros cargados")
df_registros.head()
#4
df_cuadro = pd.read_excel(nombre_excel, usecols=[0, 12], header=0)
df_cuadro.columns = ['Motivo', 'Emergencia_Cuadro']
df_cuadro['Motivo'] = df_cuadro['Motivo'].astype(str).str.strip().str.zfill(4)

print(f"✅ {len(df_cuadro)} motivos en el cuadro")
df_cuadro.head()
#5
df_resultado = df_registros.merge(df_cuadro, on='Motivo', how='left')

# Columna de validación: ¿coinciden?
def validar(row):
    em_txt = row['Aplica_Emergencia_Economica']
    em_cuadro = str(row['Emergencia_Cuadro']).strip().upper()
    if em_cuadro in ['SI', 'SÍ', 'YES', '1']:
        esperado = '1'
    elif em_cuadro in ['NO', '0']:
        esperado = '0'
    else:
        return 'Sin dato en cuadro'
    return '✅ OK' if em_txt == esperado else '❌ Diferencia'

df_resultado['Validacion'] = df_resultado.apply(validar, axis=1)

# Reordenar columnas para que quede legible
cols = [
    'Motivo',
    'Tipo_Movimiento', 'Tipo_Movimiento_Desc',
    'Aplica_Emergencia_Economica',
    'Emergencia_Cuadro',
    'Validacion',
    'Val_Inactividad',
    'Linea_Original'
]
df_resultado = df_resultado[cols]

# Exportar
df_resultado.to_excel('resultado_validacion.xlsx', index=False)
files.download('resultado_validacion.xlsx')
print("✅ Archivo descargado: resultado_validacion.xlsx")
#who knows