# Telemetria wiąże się z rejestrem urządzeń przez `external_id`, bez klucza obcego

`telemetry_packets.device_id` to `String(128)` przechowujący `Device.external_id` (numer seryjny), a nie `UUID` z kluczem obcym do `devices.id`. Klucze obce w obrębie modułu telemetrii istnieją i działają (`telemetry_errors.packet_id` → `telemetry_packets.id`, `ondelete=CASCADE`); nie ma ich wyłącznie **przez granicę modułu**.

## Status

Proposed

## Kontekst

Pakiet przychodzi z urządzenia i identyfikuje się numerem seryjnym — to jedyny identyfikator, który urządzenie o sobie zna. Zapisanie go pod `devices.id` wymagałoby rozwiązania numeru seryjnego na UUID przy każdym ingeście i związania zapisu pomiaru z istnieniem wiersza w rejestrze.

## Decyzja

Strumień pomiarowy jest przechowywany pod tym identyfikatorem, którym posługuje się urządzenie, i nie zależy od rejestru na poziomie schematu bazy. Rejestr jest sprawdzany w kodzie (`TelemetryPacketRepository.create` odrzuca pakiet nieznanego urządzenia przez `NotFoundError`), ale nie przez constraint.

## Rozpatrywane alternatywy

- **FK `device_id` → `devices.id`** — daje integralność i darmowe kaskadowe kasowanie, ale wiąże moduł zapisu pomiarów z modułem rejestru na poziomie schematu i utrudnia ewentualne wydzielenie telemetrii do osobnej bazy (tabela `telemetry_packets` rośnie inaczej niż reszta).

## Konsekwencje

- **Kasowanie musi być jawne.** `DeviceLifecycleService` usuwa pakiety osobnym wywołaniem, z komentarzem „no FK, must be explicit". Każda nowa ścieżka kasowania urządzenia musi o tym pamiętać, bo baza nie przypomni.
- Możliwe są pakiety-sieroty, jeśli ktoś skasuje urządzenie z pominięciem orkiestratora.
- Numer seryjny staje się w praktyce niezmienny: zmiana `Device.external_id` odcięłaby całą historię pomiarową. Dziś nic tego nie zabrania — warto rozważyć zakaz na poziomie serwisu.
- Zysk: ingest jest odporny na stan rejestru i tani (jeden `SELECT` po indeksowanym `external_id`, bez joinów), a tabela pomiarowa może zostać kiedyś odseparowana bez rozplątywania kluczy obcych.
