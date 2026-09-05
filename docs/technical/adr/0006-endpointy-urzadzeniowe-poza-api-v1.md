# Endpointy konsumowane przez firmware stoją poza `/api/v1` i nie są wersjonowane

`/telemetry/ingest`, `/devices/auth/challenge`, `/devices/auth/verify`, `/devices/activation/redeem` i `/auth/*` są montowane bez prefiksu wersji. Wszystko, co konsumuje frontend, siedzi pod `/api/v1`. Ścieżki urządzeniowe są zaszyte w firmware jako stałe w `firmware/include/Config.h`.

## Status

Proposed

## Kontekst

Wersjonowanie API służy temu, żeby móc zmienić kontrakt bez psucia klientów. Ten mechanizm działa tylko wtedy, gdy klienta da się zaktualizować. Urządzenie zamontowane w przepompowni na wsi aktualizuje się przez wizytę serwisanta albo OTA przez modem GSM — w obu przypadkach to nie jest operacja, którą da się zrobić „przy okazji deploya".

## Decyzja

Ścieżki urządzeniowe traktujemy jako **stały, niewersjonowany kontrakt**. Wersjonowanie protokołu przenosimy do treści pakietu: `MeasurementPacketRequest.v` jest polem obowiązkowym z ograniczeniem `Field(ge=2, le=2)`, więc niezgodność wersji wychodzi jako 422 na walidacji, a nie jako 404 na nieistniejącej ścieżce.

`/auth/*` jest w tej samej grupie z innego powodu: to ścieżka logowania, stabilna dla wszystkich klientów naraz.

## Konsekwencje

- Zmiana ścieżki urządzeniowej wymaga flashowania sprzętu w terenie. Praktycznie: **te ścieżki są nieodwracalne**.
- Rozszerzenie protokołu telemetrycznego idzie przez podniesienie `v` i rozszerzenie zakresu w `Field(ge=…, le=…)`, a nie przez `/api/v2/telemetry/ingest`.
- Konsekwencją uboczną jest to, że OpenAPI pokazuje dwie rodziny ścieżek o różnych konwencjach. Warto, żeby nowy endpoint trafiał domyślnie pod `/api/v1` — poza `/api/v1` idzie tylko to, co ma po drugiej stronie urządzenie.
