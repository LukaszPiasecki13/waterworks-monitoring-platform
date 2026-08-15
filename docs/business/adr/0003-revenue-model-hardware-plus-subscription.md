# Model finansowy: hardware (one-time) + subskrypcja (monthly)

Dochodowy model biznesu: gmina płaci **jednorazowo za sprzęt i wdrożenie**, potem **miesięczny abonament za platformę, SIM i serwis**. Szczegóły rozliczenia kanałów (per-czujnik vs ryczałt) otwarte — będą ustalane adaptacyjnie z klientami.

## Status
Accepted

## Kontekst
Szacunki kosztów jednostkowych (patrz [01_plan_biznesowy.md, rozdział 4.2](../01_plan_biznesowy.md#42-szacunek-kosztów-jednostkowych)): sprzęt to 1,4–3,5 tys. PLN, wdrożenie to 1,5–4,8 tys. PLN, opex to 0,5–1,3 tys. PLN rocznie. To sugeruje model: klient płaci za sprzęt i instalację, my dostajemy przychód z abonamentu.

Biorąc pod uwagę:
- **Rozmiar rynku**: 1300–1700 potencjalnych gmin — nigdy nie będziemy mieć tysiąca klientów, to lokalny biznes
- **Ambicja**: zorientowana na klienta, organiczna, długoterminowe relacje — nie wzrost za wszelką cenę

Model hardware + subskrypcja zmienia dynamikę: każdy nowy klient to nasza inwestycja w sprzęt i wdrożenie, potem stały przychód (abonament). To zmienia rentowność w kierunku: szukamy klientów, którzy zostają, a nie klientów, którzy szybko odchodzą.

## Decyzja
1. **Koszt dla klienta (Gminy)**:
   - **One-time**: sprzęt (gateway, czujniki, kable, obudowa) + montaż (inwentaryzacja, instalacja, testy)
   - **Monthly**: abonament za platformę, dostęp do dashboardu, alarmy, SIM, serwis, retencja danych

2. **Szczegóły otwarte** (do ustalenia z klientami):
   - Czy dodatkowe kanały (temperatura, ciśnienie, poziom, pompa, chlor…) są wliczone w abonament?
   - Czy każdy kanał ma osobną opłatę (per-kanał model)?
   - Czy jest pakiet bazowy X kanałów w cenie, potem upsell?
   - → **Decyzja**: Startujemy z elastycznym negocjowaniem per-klient, zbieramy doświadczenie, potem standaryzujemy cennik w Phase 2.
   - **Otwarte i nierozstrzygnięte przez ten ADR**: jaka jest nasza marża na sprzęcie i wdrożeniu (dziś cena w dokumencie 04 jest ustawiona równo kosztowi — czyli marża zero, co nie jest świadomą decyzją, tylko brakiem decyzji). Wymaga ustalenia realnego narzutu, zanim cennik pójdzie do pierwszego płatnego klienta.

3. **Własność**: Gmina kupuje sprzęt (posiada go), my utrzymujemy usługę software'ową.

## Rozpatrywane alternatywy
- **Sprzęt w abonamencie**: gmina płaci wyższy abonament, my posiadamy sprzęt i czuwamy nad nim. Zmniejsza barierę wejścia dla gminy, ale zwiększa nasz koszt operacyjny i komplikuje logistykę wymiany sprzętu. Może być opcją dla Phase 2, gdy będziemy mieć więcej klientów.
- **Tylko SaaS (bez sprzętu)**: gmina kupuje sprzęt samodzielnie, my dostarczamy platformę. Zbyt wąskie — gminy nie będą wiedzieć, jaki sprzęt wybrać, a my stracilibyśmy kontrolę nad integracją.

## Konsekwencje
- **Pierwszy rok każdego klienta**: w przybliżeniu neutralny na transakcji sprzęt+wdrożenie — *pod warunkiem*, że cena rzeczywiście pokrywa nasz koszt (dziś nieustalone, patrz pkt 2 wyżej). Abonament jest czystym przychodem od pierwszego miesiąca, jeszcze przed odliczeniem czasu założycieli i kosztów stałych firmy.
- **Rok 2+**: dodatni — koszty operacyjne (SIM, chmura, serwis) są niższe niż przychód z abonamentu.
- **Cash flow**: będzie wymagać buforu — musimy pokryć wdrożenie pierwszych klientów z budżetu bootstrap, zanim wpłynie ich jednorazowa opłata.
- **Cennik**: będziemy negocjować indywidualnie; nie będzie publicznego kalkulatora ceny (staje się przeszkodą w sprzedaży dla małych gmin).

## Notatki
- Skorygowany rachunek (patrz [01_plan_biznesowy.md, rozdział 4.2.7](../01_plan_biznesowy.md#427-rentowność-obiektu)) pokazuje, że przy cenie jednorazowej ustawionej na poziomie kosztu (dzisiejszy stan — zero marży, patrz rozdział 4.1.1) transakcja sprzęt+wdrożenie jest w przybliżeniu neutralna dla gotówki, a margines na abonamencie jest dodatni od pierwszego roku (~460–1300 zł/obiekt/rok, zależnie od scenariusza kosztowego).
- To NIE jest marża operacyjna całej firmy — nie uwzględnia czasu założycieli ani kosztów stałych. Rzetelny próg rentowności firmy wymaga osobnego modelu finansowego (P&L), którego jeszcze nie mamy.

