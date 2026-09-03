# `transaction()` jest jedyną granicą transakcji, a repozytoria nigdy nie commitują

Jednostkę pracy otwiera serwis przez `with self.repo.transaction():`. Repozytoria wykonują wyłącznie `add`/`flush`/`delete` — commit i rollback należą do właściciela transakcji.

## Status
Proposed

## Kontekst
36 ścieżek zapisu w pięciu modułach używa `SQLRepository.transaction()`; poza `cli.py` (skrypt startowy, nie warstwa HTTP) jedynym ręcznym commitem jest seed uprawnień. Repozytoria mówią to wprost w docstringach: *„Flushes rather than commits: the transaction belongs to the caller"* ([`packets.py:36-38`](../../../backend/app/modules/telemetry/repositories/packets.py#L36-L38), [`device_credentials.py:56`](../../../backend/app/modules/device_identity/repositories/device_credentials.py#L56)).

## Decyzja
`transaction()` ([`repository.py:34-49`](../../../backend/app/infrastructure/sql/repository.py#L34-L49)) commituje po bezusterkowym wyjściu z bloku i robi rollback + re-raise przy dowolnym wyjątku. Dzięki temu operacja obejmująca kilka repozytoriów, a nawet kilka modułów, jest atomowa bez koordynacji między nimi — tak działa kaskadowe usunięcie urządzenia ([`device_lifecycle.py:49-71`](../../../backend/app/modules/core_data/services/device_lifecycle.py#L49-L71)), które w jednej transakcji kasuje telemetrię, rekord urządzenia i credential.

Konsekwencją jest reguła negatywna: serwis nie dotyka `session` ani `commit()`/`rollback()` bezpośrednio. Cztery miejsca, które to dziś łamią, są opisane jako dług w [`07_analiza_paradygmatow.md`](../backend/07_analiza_paradygmatow.md) — w tym `session.rollback()` wywołany wewnątrz cudzej transakcji w [`measurement_points.py:183`](../../../backend/app/modules/core_data/services/measurement_points.py#L183).

## Konsekwencje
- Zagnieżdżenie `transaction()` w `transaction()` nie tworzy savepointu — wewnętrzny blok zacommituje całość. Serwis wołany z wnętrza cudzej transakcji musi być „bezcommitowy" i mówić to w docstringu, jak [`delete_device_record`](../../../backend/app/modules/core_data/services/devices.py#L257-L266).
- `tx.skip_audit()` jest częścią tego samego uchwytu, bo decyzja „ta transakcja nie generuje audytu" zapada w miejscu, w którym serwis wie, że nie ma czego zapisać (ADR-0002).
