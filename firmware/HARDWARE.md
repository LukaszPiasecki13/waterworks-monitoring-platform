# Mapa sprzętowa gatewaya

Źródło prawdy dla fizycznych połączeń ESP32-S3. Przed dotknięciem GPIO — sprawdź tutaj, nie zgaduj.

## 1. Komponenty

- **ESP32-S3-DevKitC-1** — główny mikrokontroler
- **A7670E** — modem LTE-M (UART)
- **PT-506** — czujnik ciśnienia, wyjście 4-20mA
- **PT100 + MAX31865** — czujnik temperatury (RTD przez konwerter SPI)

## 2. Piny

| GPIO | Funkcja | Podłączone do | Uwagi |
|---|---|---|---|
| 17 | UART1 TX | A7670E RX | [`Config.h`](include/Config.h) |
| 18 | UART1 RX | A7670E TX | [`Config.h`](include/Config.h) |
| 4 | PWRKEY | A7670E | [`Config.h`](include/Config.h) |
| 5 | RESET | A7670E | [`Config.h`](include/Config.h) |
| 1 | ADC1_CH0 | PT-506 (4-20mA) | przez rezystor 250Ω |
| 12 | SPI SCK | MAX31865 | |
| 11 | SPI MOSI | MAX31865 | |
| 13 | SPI MISO | MAX31865 | |
| 10 | SPI CS | MAX31865 | |

## 3. Interfejsy

- **Pętla 4-20mA (PT-506)**: prąd zamieniany na napięcie rezystorem 250Ω przed wejściem ADC.
- **SPI (PT100/MAX31865)**: standardowe 4-wire SPI, jedno urządzenie na magistrali.
- **Weryfikacja**: piny czujników (1, 10, 11, 12, 13) są draftem — do potwierdzenia na fizycznej płytce przed lutowaniem (część GPIO na ESP32-S3-DevKitC-1 może być zajęta pod PSRAM/flash lub pełnić funkcję strappingową, zależnie od wariantu modułu).
