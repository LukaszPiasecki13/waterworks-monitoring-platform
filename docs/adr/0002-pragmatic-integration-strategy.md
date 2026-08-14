# Strategia integracji: pragmatyczne podłączanie się do istniejących systemów

Zamiast deklarować sztywną listę obsługiwanych protokołów (Modbus RTU, Modbus TCP, 4-20 mA, itp.), **adaptujemy się do tego, co każda gmina już ma zainstalowane**. Jeśli coś się podpiąć da łatwo, robimy; jeśli wymaga custom pracy, dokumentujemy i ewentualnie wyceniamy osobno.

## Status
Accepted

## Kontekst
Każda gmina ma inną infrastrukturę: inne PLC, inne przepływomierze, inne interwały rejestracji danych. **Największym ryzykiem nie jest brak protokołów, tylko integracja z tym, co gmina już ma**. Gminy rzadko mówią „mamy Modbus", lecz raczej „mamy stary PLC od Siemensa z nieznaną dokumentacją".

## Decyzja
1. **Nie definiujemy sztywnej listy obsługiwanych urządzeń** — byłaby to fałszywa obietnica uniwersalności, a klienci byliby rozczarowani, gdy ich stary PLC nie wchodzi.
2. **Proces na każdy obiekt: inwentaryzacja → diagnoza → decyzja**
   - Kiedy montujemy u nowego klienta, najpierw zbieramy informacje: PLC, przepływomierz, czujniki, dostępne interfejsy (Modbus, 4-20 mA, impulsy, styki).
   - Jeśli interfejs się pokrywa z tym, co obsługujemy (Modbus RTU, 4-20 mA, impulsy licznikowe — szacunkowo, bez twardych danych, większość gmin), procesujemy normalnie.
   - Jeśli wymaga adaptera, custom kodu, czy dodatkowych modułów, robimy to z gminą jako osobny, płatny projekt lub negocjujemy w kontrakcie wdrażania.
3. **Profil urządzenia**: Gdy się uda, mapowanie (PLC model → profile) dokumentujemy jako profil wielokrotnego użytku dla przyszłych gmin.

## Rozpatrywane alternatywy
- **Sztywna lista: obsługujemy A, B, C, nic więcej**: bezpieczne biznesowo, ale zamyka drzwi klientom, którzy mają X, Y, Z. Odrzucone.
- **Deklarujemy uniwersalność: robimy wszystko, każda integracja**: oszukaństwo marketingowe, prowadzi do niekontrolowanego kosztu i rozczarowania klienta. Odrzucone.

## Konsekwencje
- **Proces wdrożenia**: każdy obiekt wymaga indywidualnej fazy diagnozy (inwentaryzacji) — to nie jest plug-and-play.
- **Cennik**: będziemy mieć model wdrożenia, w którym integracja standardowa (Modbus, 4-20 mA) wchodzi w koszt; integracja niestandardowa to osobny projekt.
- **Architektura**: firmware i backend muszą obsługiwać profile urządzeń konfigurowalnie (nie hardcoded dla każdego PLC modelu).
- **Referencje**: każdy nowy typ PLC, który uda się zintegrować, trafia do bazy profili — kolejne gminy z tym samym sprzętem mają ułatwienie.

## Notatki
- [01_plan_biznesowy.md, rozdział 3.3](../01_plan_biznesowy.md#33-integracja-z-istniejącą-automatyką) już zawiera checklist inwentaryzacji — to jest procedura do formalizacji.
- [01_plan_biznesowy.md, rozdział 5.2.7](../01_plan_biznesowy.md#527-możliwa-przewaga-konkurencyjna-projektowanego-systemu) zawiera ideę profili urządzeń zamiast dedykowanego kodu — to strategia wspierająca pragmatyczną integrację.

