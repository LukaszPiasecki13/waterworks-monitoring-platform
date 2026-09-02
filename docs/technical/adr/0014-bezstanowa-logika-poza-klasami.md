# Logika bezstanowa mieszka w funkcjach modułowych, a kontekst operacji w zamrożonej dataclass

Kod, który nie potrzebuje wstrzykniętych zależności, nie dostaje klasy. Wartości przekazywane między warstwami i pomocnikami są niemutowalnymi dataclassami, nie słownikami ani listami argumentów.

## Status
Proposed

## Kontekst
Template modułu ([`01_backend-architecture.md` §5.2](../backend/01_backend-architecture.md)) pokazuje serwis jako klasę z repozytorium w `__init__` — i tak wygląda każdy serwis, który faktycznie coś wstrzykuje. Tam, gdzie nie ma czego wstrzykiwać, kod konsekwentnie rezygnuje z klasy: [`password.py`](../../../backend/app/modules/security/services/password.py) i [`signature.py`](../../../backend/app/modules/device_identity/services/signature.py) to moduły złożone wyłącznie z funkcji, a [`ingest.py:36-99`](../../../backend/app/modules/telemetry/services/ingest.py#L36-L99) i [`activation_codes.py:31-39`](../../../backend/app/modules/device_identity/services/activation_codes.py#L31-L39) trzymają czyste transformacje poza klasą serwisu. Symetrycznie, wszystkie konteksty przekazywane dalej są zamrożone: `AuditEntry` (`frozen=True, slots=True`), `OrganizationAccess`, `PlatformContext`, `_IngestContext`, `PermissionDef`.

## Decyzja
- Funkcja, której ciało nie sięga po `self`, zostaje funkcją modułową (prywatną, jeśli służy tylko temu plikowi).
- Zestaw wartości przewlekany przez kilka funkcji jest `@dataclass(frozen=True)`, a nie `dict` ani rosnąca lista parametrów.

## Rozpatrywane alternatywy
- **`@staticmethod` w klasie serwisu**: trzyma wszystko razem, ale sugeruje zależność od instancji, której nie ma, i utrudnia użycie z innego modułu. Używane tylko dla strażników operujących na argumencie klasy (`GroupService._ensure_custom_group`).
- **Słownik jako kontekst**: brak podpowiedzi typów, brak ochrony przed przypadkową mutacją w połowie przetwarzania pakietu.

## Konsekwencje
- Funkcje modułowe testuje się bez konstruowania serwisu i bez mocków — `verify_signature`, `hash_password`, `_iter_points` mają testy jednostkowe wprost.
- Kod czytający `services/<x>.py` musi się liczyć z tym, że nie zawsze znajdzie tam klasę — to świadome odstępstwo od template'u, nie niedokończony refaktor.
