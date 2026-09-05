# Aktorem w logu audytu jest napis bez klucza obcego, bo urządzenie też jest aktorem

`AuditEvent.actor_id` to `String(255)` bez FK do `users`, a `actor_display_name` to wolny tekst. Powodem nie jest niedbałość, tylko to, że część zdarzeń audytowych powstaje **bez udziału użytkownika**: pierwszy claim urządzenia i redempcja kodu aktywacyjnego zapisują `actor_id = str(credential.id)` i `actor_display_name = f"device:{serial_number}"`.

## Status

Proposed

## Kontekst

Rejestracja urządzenia w terenie to zdarzenie, które musi zostać w niezmiennym logu — inaczej nie da się później odpowiedzieć na pytanie „kiedy i jakim kodem to urządzenie weszło do systemu". Za tym zdarzeniem nie stoi jednak żaden użytkownik: urządzenie samo wywołuje `/devices/activation/redeem`, a potem `/devices/auth/verify`.

## Decyzja

Aktor jest identyfikatorem tekstowym, a nie referencją. Konwencja zapisu:

| Rodzaj aktora | `actor_id` | `actor_display_name` |
|---|---|---|
| użytkownik | `str(user.id)` | `user.email` |
| urządzenie | `str(credential.id)` | `device:{serial_number}` |

## Rozpatrywane alternatywy

- **FK do `users` + osobna tabela na aktorów nie-ludzi** — poprawne relacyjnie, ale wprowadza join na każdym odczycie historii i drugą tabelę do utrzymania dla dwóch typów aktora.
- **Sztuczne konto techniczne „system"** — traci informację, *które* urządzenie się zarejestrowało; w logu wszystkie zlewałyby się w jedno.

## Konsekwencje

- Brak integralności referencyjnej: skasowanie użytkownika nie unieważnia jego wpisów w audycie. Dla append-only logu to **cecha**, nie wada — historia ma przetrwać usunięcie konta.
- `actor_display_name` jest zamrożonym snapshotem, nie referencją: e-mail zapisany w logu nie zmienia się, gdy użytkownik zmieni adres. Zamierzone.
- Konsument logu musi rozpoznawać aktorów po prefiksie `device:` w `actor_display_name`. To jedyna rzecz, która odróżnia oba rodzaje — warto o tym pamiętać, projektując widok historii.
