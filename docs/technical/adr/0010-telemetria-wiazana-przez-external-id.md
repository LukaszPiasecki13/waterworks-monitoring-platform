# Telemetria wiąże się z urządzeniem przez `external_id`, bez klucza obcego

`telemetry_packets.device_id` i `telemetry_errors.device_id` to numer seryjny urządzenia (`String(128)`), nie klucz obcy do `devices.id`. Dane pomiarowe nie mają referencyjnej zależności od rejestru urządzeń.

## Status
Proposed

## Kontekst
Pakiet z terenu identyfikuje siebie numerem seryjnym — to jedyny identyfikator, który zna firmware. Modele nie deklarują `ForeignKey` ([`measurement_packet.py:32`](../../../backend/app/modules/telemetry/models/measurement_packet.py#L32), [`telemetry_error.py:35`](../../../backend/app/modules/telemetry/models/telemetry_error.py#L35)), a operacje na telemetrii posługują się numerem seryjnym również po stronie kodu (`delete_all_for_device(external_id)`). Odróżnia to telemetrię od `measurement_points`, które mają twardy `ForeignKey("devices.id", ondelete="CASCADE")`.

## Decyzja
Log pomiarowy jest niezależny od cyklu życia rekordu urządzenia. Usunięcie urządzenia nie kasuje telemetrii kaskadą — musi ją skasować jawnie orkiestrator ([`device_lifecycle.py:51`](../../../backend/app/modules/core_data/services/device_lifecycle.py#L51)), w tej samej transakcji.

## Rozpatrywane alternatywy
- **`ForeignKey` na `devices.id`**: baza gwarantuje spójność i kasuje kaskadą, ale pakiet od urządzenia jeszcze nierozpoznanego nie miałby gdzie trafić, a wymiana rekordu urządzenia zabierałaby ze sobą historię pomiarów. Odrzucone.

## Konsekwencje
- Osierocone pakiety są możliwe: baza ich nie zablokuje. Kasowanie musi być wykonane w kodzie i przetestowane — dziś robi to `DeviceLifecycleService`.
- Ingest i tak sprawdza istnienie urządzenia przed zapisem pakietu ([`packets.py:40-49`](../../../backend/app/modules/telemetry/repositories/packets.py#L40-L49)), więc integralność jest pilnowana w aplikacji, nie w schemacie.
- Zapytania telemetryczne łączą się z `core_data` przez `external_id`, co wymaga joinu po kolumnie tekstowej — indeks `ix_telemetry_packets_device_id` jest tu obowiązkowy, nie opcjonalny.
