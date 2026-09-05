# Dwie płaszczyzny dostępu to dwa osobne routery na ten sam zasób, a nie jeden z rozgałęzieniem

Zasób wystawiony i gminie, i operatorowi platformy ma **dwa routery w jednym pliku**: `router` z prefiksem `/orgs/{org_id}/<zasób>` i uprawnieniami `CAN_*`, oraz `platform_router` z prefiksem `/<zasób>` i uprawnieniami `PLATFORM_*`. Prefiks `/api/v1/platform` dokleja się dopiero przy montażu w `main.py`. Tak zrobione są `devices`, `water_objects`, `users` i `activation_codes`.

## Status

Proposed

## Kontekst

Ten sam obiekt — urządzenie — jest widziany zupełnie inaczej z dwóch stron: gmina widzi swoje urządzenia i może je odpiąć; operator platformy widzi wszystkie i może skasować całkowicie. Różnią się nie tylko uprawnienia, ale zasięg zapytania, kształt odpowiedzi i semantyka `DELETE` (odpięcie vs. kasacja kaskadowa).

## Decyzja

Rozdzielić na poziomie routera, nie warunku w handlerze. Konsekwencje tego wyboru widać w kodzie: `DELETE /orgs/{org_id}/devices/{id}` woła `DeviceService.detach_from_organization`, a `DELETE /platform/devices/{id}` woła `DeviceLifecycleService.delete_device_completely` — dwie różne operacje pod tą samą metodą HTTP.

## Rozpatrywane alternatywy

- **Jeden router, rozgałęzienie po uprawnieniu w handlerze** — mniej kodu, ale ten sam URL zaczyna znaczyć dwie różne rzeczy zależnie od tego, kto pyta. Przy `DELETE` to różnica między odpięciem a nieodwracalną kasacją danych pomiarowych. Odrzucone.
- **Osobne moduły `platform_*`** — pełne rozdzielenie, ale duplikuje serwisy i schematy dla tych samych encji. Odrzucone.

## Konsekwencje

- Katalog uprawnień jest podzielony na dwie rozłączne przestrzenie, a `PermissionService.resolve_permissions` tego pilnuje: grupa platformowa może zawierać wyłącznie kody `PLATFORM_*`, grupa organizacyjna wyłącznie `CAN_*`.
- Dodanie zasobu widocznego z obu stron oznacza dwa routery i dwa komplety uprawnień — więcej pisania, ale zero niejednoznaczności w tym, co robi dany URL.
- Użytkownik może być jednocześnie członkiem gminy i adminem platformy; to dwie niezależne role, a nie hierarchia. Admin platformy bez członkostwa **nie widzi** danych pomiarowych gminy.
