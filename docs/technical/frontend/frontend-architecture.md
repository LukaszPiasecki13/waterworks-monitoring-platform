# Architektura Frontendu — Dokumentacja Techniczna

> Odpowiednik frontendowy dokumentu [`01_backend-architecture.md`](../backend/01_backend-architecture.md).

## Spis treści

- [Architektura Frontendu — Dokumentacja Techniczna](#architektura-frontendu--dokumentacja-techniczna)
  - [Spis treści](#spis-treści)
  - [1. Stack technologiczny](#1-stack-technologiczny)
  - [2. Struktura katalogów](#2-struktura-katalogów)
  - [4. Zarządzanie stanem klienta](#4-zarządzanie-stanem-klienta)
  - [5. Warstwa danych: services → hooks → React Query](#5-warstwa-danych-services--hooks--react-query)
  - [6. Wspólny stan formularzy CRUD — `useCrudPageState`](#6-wspólny-stan-formularzy-crud--usecrudpagestate)
  - [7. Stan serwerowy i cache](#7-stan-serwerowy-i-cache)
  - [8. Cykl sesji użytkownika](#8-cykl-sesji-użytkownika)
  - [9. Obsługa zimnego startu backendu](#9-obsługa-zimnego-startu-backendu)
  - [10. Responsywność i dostępność](#10-responsywność-i-dostępność)
  - [11. Testowanie](#11-testowanie)

---

## 1. Stack technologiczny

| Warstwa | Technologia |
|---|---|
| Framework UI | React + TypeScript, build przez Vite |
| Routing | `react-router-dom` (v7), `createBrowserRouter` |
| Stan serwerowy / cache | TanStack React Query |
| Stan klienta | Zustand + middleware `persist` (localStorage) |
| HTTP | Axios (dwa dedykowane klienty, patrz sekcja 5) |
| Stylowanie | Tailwind CSS |

## 2. Struktura katalogów

```text
frontend/src/
├─ App.tsx                # drzewo tras (createBrowserRouter) + providery (QueryClientProvider)
├─ pages/                  # widoki tras — jeden plik na stronę
├─ components/
│  ├─ ui/                  # prymitywy design systemu: Button, Dialog, DataTable, Toast...
│  ├─ layout/              
│  │  ├─ OrgShell.tsx       # shell dla płaszczyzny organizacji (zawiera Topbar+OrgSidebar+main)
│  │  ├─ PlatformShell.tsx  # shell dla płaszczyzny platformy (lazy-loaded, React.lazy)
│  │  ├─ OrgSidebar.tsx     # sidebar organizacyjny (Monitoring, Konfiguracja, Admin z Członkami/Grupami)
│  │  ├─ PlatformSidebar.tsx # sidebar platformowy (Organizacje, Użytkownicy, Grupy, Audyt)
│  │  ├─ EnvironmentSwitcher.tsx  # switcher gminy/platformy (ukryty gdy tylko 1 środowisko)
│  │  ├─ Topbar.tsx         # wspólny topbar dla obu płaszczyzn
│  ├─ dialogs/              # formularze create/edit per encja (DeviceFormDialog, UserFormDialog...)
│  ├─ dashboard/, objects/, security/   # komponenty domenowe per obszar
│  ├─ ProtectedRoute.tsx, RequirePermission.tsx   # guardy tras
│  └─ BackendWakeupPopup.tsx
├─ hooks/                   # useQuery/useMutation per zasób (useDevices, useUsers, ...)
│  ├─ queryKeys.ts           # centralna fabryka kluczy React Query
│  ├─ useActivePermissions.ts   # jedyne źródło prawdy: uprawnienia w aktywnym środowisku
│  ├─ useMembers.ts, useOrgGroups.ts, usePlatformGroups.ts, usePlatformAudit.ts   # org/platform hooks
│  └─ useCrudPageState.ts     # wspólny stan formularzy CRUD (sekcja 6)
├─ services/                  # cienkie wrappery Axios per zasób REST
├─ stores/                     
│  ├─ authStore.ts             # użytkownik, tokeny, userContext (M:N członkostw + uprawnienia per gmina)
│  └─ activeEnvironmentStore.ts # wybrane środowisko: org {id, name} czy platform
├─ lib/                         # api.ts, queryClient.ts, sessionLifecycle.ts, backendWakeup.ts, errors.ts
├─ types/                        # typy DTO (coreData, telemetry, security, permissions, context)
└─ styles/                        # tokens.css
```

Konwencja warstw danych: `pages/` konsumują `hooks/`, `hooks/` opakowują `services/` w React Query, `services/` jako jedyna warstwa woła `apiClient`/`authClient` z `lib/api.ts`. Wyjątek: `LoginPage` wołuje `authService.getMyContext()` bezpośrednio — zalogowanie wymagapobrania kontekstu użytkownika (mamy środowiska).

**Lazy loading płaszczyzn**: `OrgShell` i `PlatformShell` są owinięte w `React.lazy()` w `App.tsx` — kod mapy, telemetrii, widoków organizacyjnych (org-plane) nie trafia do bundla super admina wchodzącego tylko na `/platform/...`.


## 4. Zarządzanie stanem klienta

Dwa store'y Zustand, oba z middleware `persist`:

- **`authStore`** — `user` (id, username, email, first/last name), `userContext` (środowiska + uprawnienia per gmina, moje grupy na platformie), `accessToken`/`refreshToken`, `isAuthenticated`. Uprawnienia NIE są przechowywane jako płaska lista (`permissions`/`groupIds`) — tylko w `userContext` per-środowisko. `logout()` jest jedynym poprawnym punktem czyszczenia sesji (patrz sekcja 8). `setUserContext()` wywoływane po `/auth/me/context` lub refreshu tokenu.
- **`activeEnvironmentStore`** — wybrane środowisko (discriminated union): `{ type: 'organization'; organizationId: string; organizationName: string }` albo `{ type: 'platform' }`. `setOrganization({id, name})`, `setPlatform()`, `clear()`. Czyszczony przez `authStore.logout()`. Persystowany pod kluczem `active-environment` (stary klucz `active-organization` jest historyczny relikt).

## 5. Warstwa danych: services → hooks → React Query

- **`services/<resource>Service.ts`** — cienkie wrappery `apiClient` per zasób REST. Nowe serwisy dla modelu dwupłaszczyznowego: `membersService`, `orgGroupsService`, `platformAuditService`, `platformGroupsService`. Istniejące serwisy (`usersService`, `organizationsService`, `waterObjectsService`, itd.) zostały naprawione — URL-e wskazują na `/api/v1/platform/` (użytkownicy/organizacje) albo `/api/v1/orgs/{orgId}/` (zasoby gmin). Zwracają rozpakowane dane (wyciągają `items` z paginowanej odpowiedzi).
- **`hooks/use<Resource>.ts`** — opakowują `services/` w `useQuery`/`useMutation`. Nowe hooki dla dwupłaszczyznowości: `useMembers(orgId)`, `useOrgGroups(orgId)`, `usePlatformGroups()`, `usePlatformAudit(params)`. Hooki org-plane i platform-plane żyją w **osobnych plikach** (bez barrel-exportu razem), żeby `React.lazy(OrgShell)`/`React.lazy(PlatformShell)` faktycznie rozdzieliły bundle.
- **`hooks/useActivePermissions()`** — jedyne źródło prawdy o uprawnieniach w aktywnym środowisku. Czyta `authStore.userContext` + `activeEnvironmentStore.environment`, zwraca `{ permissions, hasPermission(p), hasAnyPermission(ps) }`. Fail-closed: brak środowiska lub brak `userContext` = pusta lista uprawnień (→ `/forbidden`).
- `lib/api.ts` eksportuje dwa klienty Axios: `authClient` (bez interceptora — logowanie, refresh) i `apiClient` (z interceptorami: zimny start backendu, nagłówek `Authorization`, refresh 401, 404 na `/api/v1/orgs/*` → `NotFoundPage`).
- **`deviceStateService` / `useDeviceState`** — odczyt stanu urządzenia (B-08). Jedyny hook z `refetchInterval`, bo odpowiedź zmienia się dopiero przy następnym kontakcie urządzenia; odpytywanie co minutę jest tym, co zamienia „nieświeże" w „świeże" bez przeładowania strony. Formatowanie wieku, uptime'u i progów RSSI żyje w `lib/deviceState.ts`, żeby zasada „nigdy nie pokazuj wartości bez czasu" miała jedną implementację, a nie po jednej na widok. Kanał opisany przekrojowo: [`01_kanal_stanu_urzadzenia.md`](../01_kanal_stanu_urzadzenia.md).

## 6. Wspólny stan formularzy CRUD — `useCrudPageState`

Strony administracyjne (organizacje, obiekty wodociągowe, urządzenia, punkty pomiarowe, użytkownicy) współdzielą jeden generyczny hook, `hooks/useCrudPageState.ts`, zamiast każda pisać własny stan formularza od zera.

Hook przyjmuje trzy mutacje React Query (`createMutation`/`updateMutation`/`deleteMutation`) i zestaw komunikatów (`CrudMessages`), a zwraca kompletny stan UI strony CRUD: otwarcie/zamknięcie formularza, tryb create/edit (`editingId`), potwierdzenie usunięcia (`deleteId` + `requestDelete`/`cancelDelete`/`confirmDelete`), błędy pól zwrócone przez backend (`serverFieldErrors`, sparsowane przez `parseApiError`) oraz toasty sukcesu/błędu po każdej operacji.

Nowa strona administracyjna CRUD powinna korzystać z tego hooka zamiast duplikować jego logikę.

## 7. Stan serwerowy i cache

- React Query obsługuje dane pobierane z backendu.
- Aplikacja używa jednej instancji `QueryClient` z
  `frontend/src/lib/queryClient.ts`.
- Komponenty i store nie powinny tworzyć dodatkowych globalnych klientów.

## 8. Cykl sesji użytkownika

- `useAuthStore.logout()` jest wspólnym punktem ręcznego i automatycznego
  wylogowania.
- Logout usuwa tokeny, profil użytkownika, cały Query Cache i aktywne komunikaty
  o uruchamianiu backendu.
- Każde rozpoczęcie lub zakończenie sesji zwiększa rewizję sesji (`lib/sessionLifecycle.ts`). Odpowiedź z
  rozpoczętego wcześniej odświeżania tokenu nie może zapisać tokenów do nowej
  lub zakończonej sesji — `assertSessionUnchanged` porównuje rewizję przechwyconą przed wywołaniem `/auth/token/refresh` z aktualną i rzuca `SessionChangedError`, jeśli sesja zmieniła się w międzyczasie.
- Nowe ścieżki wylogowania muszą wywoływać akcję store zamiast samodzielnie
  usuwać wybrane klucze z `localStorage`.

## 9. Obsługa zimnego startu backendu

- Wszystkie klienty Axios komunikujące się z backendem używają interceptorów z
  `frontend/src/lib/backendWakeup.ts`.
- Po pięciu sekundach oczekiwania na pierwsze dane odpowiedzi pokazywany jest
  globalny popup informujący o zimnym starcie Rendera.
- Czas jest liczony od wysłania żądania, również dla multipart uploadu i jego
  zapytania CORS preflight. To ważne, ponieważ uśpiony Render może zatrzymać
  preflight przed rozpoczęciem wysyłania pliku.
- Pierwszy odebrany fragment odpowiedzi zamyka popup; czas pobierania całego
  pliku nie jest traktowany jako uruchamianie serwera.
- Przy wielu równoległych wolnych requestach popup znika dopiero po odpowiedzi
  ostatniego z nich.

## 10. Responsywność i dostępność

- Stylowanie odpowiada za responsywność Tailwind CSS (klasy `sm:`/`md:`/`lg:`) — nie ma osobnego, scentralizowanego dokumentu reguł układu; konwencje żyją w komponentach `components/ui/`.
- Globalny popup zimnego startu musi mieścić się na małych ekranach bez poziomego przewijania.
- Komunikat korzysta z `role="status"` i `aria-live="polite"`, aby był ogłaszany
  przez technologie asystujące bez przejmowania fokusu.

## 11. Testowanie

- Logout należy testować zarówno bezpośrednio w store, jak i przez automatyczną
  ścieżkę błędu autoryzacji.
- Interceptory wolnych requestów należy testować na instancji Axios z kontrolowaną
  odpowiedzią, w tym dla pierwszego bajtu i multipart uploadu.
- Przed mergem wymagane są: `npm test`, `npm run lint` i `npm run build`.
