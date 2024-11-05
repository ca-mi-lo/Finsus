import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Parámetros de la simulación
np.random.seed(42)  # Para reproducibilidad
n_periods = 365  # Número total de días (1 año)
forecast_days = 30  # Días de pronóstico

# Amplitudes
weekly_amplitude = 5   # Amplitud de la estacionalidad semanal
annual_amplitude = 20   # Amplitud de la estacionalidad anual

# Crear el eje de tiempo
dates = pd.date_range(start='2024-01-01', periods=n_periods + forecast_days, freq='D')
time = np.arange(len(dates))

# Componente estacional semanal
weekly_seasonal_effect = weekly_amplitude * np.sin(2 * np.pi * time / 7)

# Componente estacional anual ajustado (shifted by 91 days)
annual_seasonal_effect = annual_amplitude * np.sin(2 * np.pi * (time - 91) / 365)

# Componente aleatorio (ruido)
random_noise = np.random.normal(0, 2, n_periods + forecast_days)

# Demanda simulada total
demand = 50 + weekly_seasonal_effect + annual_seasonal_effect + random_noise  # 50 es la tendencia base

# Crear un DataFrame para manejar mejor la serie de tiempo
df = pd.DataFrame({'Date': dates, 'Demand': demand})

# Crear términos de Fourier para la estacionalidad anual
n_harmonics = 2
for i in range(1, n_harmonics + 1):
    df[f'Sin_{i}'] = np.sin(2 * np.pi * i * (time - 91) / 365)  # Shifted by 91 days
    df[f'Cos_{i}'] = np.cos(2 * np.pi * i * (time - 91) / 365)  # Shifted by 91 days

# Crear términos de Fourier para la estacionalidad semanal
for i in range(1, 2):  # One harmonic for weekly seasonality
    df[f'Week_Sin_{i}'] = np.sin(2 * np.pi * i * time / 7)
    df[f'Week_Cos_{i}'] = np.cos(2 * np.pi * i * time / 7)

# Ajustar el modelo SARIMAX con los términos de Fourier
model = SARIMAX(df['Demand'][:n_periods], 
                order=(1, 1, 1), 
                seasonal_order=(1, 1, 1, 7), 
                exog=df.iloc[:n_periods, 2:])  # Usar los términos de Fourier como variables exógenas
fitted_model = model.fit()

# Hacer pronósticos
forecast = fitted_model.forecast(steps=forecast_days, exog=df.iloc[n_periods:, 2:])

# Crear un DataFrame para los resultados del pronóstico
forecast_dates = pd.date_range(start=df['Date'][n_periods - 1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')
forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecast': forecast})

# Graficar la serie de tiempo
plt.figure(figsize=(12, 6))

# Graficar datos históricos
plt.plot(df['Date'][:n_periods], df['Demand'][:n_periods], label='Demanda Histórica', color='#cacacaff')

# Graficar datos pronosticados
plt.plot(forecast_df['Date'], forecast_df['Forecast'], label='Demanda Pronosticada', color='#FFC107', linestyle='--')

plt.title('Simulación de Demanda con SARIMAX Forecast y Fourier Terms')
plt.xlabel('Fecha')
plt.ylabel('Demanda')
plt.axhline(0, color='grey', lw=0.5, ls='--')
plt.legend()
plt.grid()
plt.show()
