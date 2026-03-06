import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de Google Sheets - Confirmar que funciona correctamente
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('config/credentials.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Trend Hunter').sheet1
sheet.update_cell(1, 1, '¡Conexión Exitosa!')
sheet.update_cell(1, 2, 'Trend Hunter Agent está listo.')
print('¡Hecho!')