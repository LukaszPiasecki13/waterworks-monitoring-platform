# MVP obejmuje temperaturę i ciśnienie; architektura projektowana pod rozszerzenia

MVP testuje dwa kanały pomiarowe: **temperatura** i **ciśnienie** na gminie pilotażowej. Architektura jest od razu projektowana tak, aby łatwo dodawać kolejne typy czujników (poziom zbiornika, praca pompy, chlor, mętność) w Phase 2, bez przebudowy systemu.

## Status
Accepted

## Kontekst
Przepływ (przepływomierz) może być dostępny u gminy pilotażowej, ale nie jest gwarancją — temperatura i ciśnienie są uniwersalne.

Jednocześnie rozszerzeń (jakość wody, poziom, pompa) chcemy wspierać, ale nie w MVP — w Phase 2, po zebraniu doświadczenia.

## Decyzja
1. **MVP zawiera**: temperatura + ciśnienie jako kanały podstawowe
2. **Architektura**: gateway, backend, frontend projektujemy od razu z myślą o tym, że będzie można dodawać kanały bez zmian firmware'u głównego (profile urządzeń, konfiguracja, mapowanie logicznych parametrów)
3. **Phase 2**: poziom zbiornika, praca pompy, jakość wody (chlor, mętność) — decyzja o kolejności odkładana na feedback z gminy pilotażowej

## Rozpatrywane alternatywy
- **Szeroki MVP od razu** (temperatura, ciśnienie, przepływ, poziom, pompa): ryzyko scope creep, wydłużenie czasu do produkcji, skomplikowanie testów. Odrzucone.
- **Tylko ciśnienie w MVP**: zbyt wąskie, temperatura jest kluczowa dla diagnostyki i bezpieczeństwa. Odrzucone.s

## Konsekwencje
- **Praktyka**: firmware, backend i frontend muszą obsługiwać rejestrację nowych typów kanałów bez hardcodowania (profile urządzeń, mapowanie, jednostki)
- **Roadmapa**: faza 2 (Phase 2) zaczyna się po stabilizacji MVP i feedback z gminy pilotażowej
- **Ryzyka**: jeśli kolejne gminy będą prosić o różne rozszerzenia jednocześnie, podejmiemy decyzje adaptacyjnie (per-klient, bez sztywnego planu)

