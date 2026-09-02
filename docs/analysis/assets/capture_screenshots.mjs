/**
 * Zbieranie biblioteki zrzutów ekranu do analizy UX konkurencji (B-03).
 *
 * Uruchamiać na maszynie z normalnym dostępem do sieci — sesja, w której powstała
 * analiza, ma egress ograniczony do hostów GitHuba i nie da się z niej otworzyć
 * żadnej z poniższych stron. Kontekst: ./README.md
 *
 *   npm install playwright sharp
 *   npx playwright install chromium
 *   node capture_screenshots.mjs [--only 07,12,21] [--width 1600] [--quality 82]
 *
 * Skrypt jest wznawialny: pomija pliki, które już istnieją. Żeby zrobić zrzut
 * ponownie, usuń plik albo dopisz --force.
 */

import { chromium } from 'playwright'
import sharp from 'sharp'
import { mkdir, readdir, rm, stat, unlink, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const OUT_DIR = dirname(fileURLToPath(import.meta.url))
const TMP_DIR = join(OUT_DIR, '.tmp')

/** Lista ujęć — kolejność i nazwy zgodne z tabelą w README.md. */
const SHOTS = [
  // --- Wod-kan i smart water ---
  ['01', 'inventia_dataportal_wizualizacja', 'https://www.inventia.pl/dataportal-jak-wizualizacja-danych-moze-ulatwic-twoja-prace/'],
  ['02', 'inventia_dataportal_scada', 'https://www.inventia.pl/przetestuj-funkcjonalnosc-dataportal-scada-bez-ponoszenia-kosztow-nowoczesna-wizualizacja-i-monitoring-danych-w-zasiegu-reki/'],
  ['03', 'dataportal_applications', 'https://dataportal.pl/en/applications/'],
  ['04', 'aquard_scada', 'https://aquard.pl/scada/'],
  ['05', 'aquard_hydranet_expert', 'https://aquard.pl/hydranet-expert/'],
  ['06', 'aquard_monitoring_sieci', 'https://aquard.pl/monitoring-sieci-wodociagowej/'],
  ['07', 'hawle_live_cap_mapa', 'https://www.hawle.com/pl/hawle-knowledge/systemy-i-rozwiazania/hawle-live-cap-rewolucja-w-monitorowaniu-hydrantow-podziemnych-na-przykladzie-hydrantu-uno'],
  ['08', 'hawle_monitoring_sieci', 'https://www.hawle.com/Monitoring_sieci_wodocigowej'],
  ['09', 'kallipr_kloud_fleet', 'https://kallipr.com/product/kallipr-kloud-fleet/'],
  ['10', 'kallipr_water_utilities', 'https://kallipr.com/industries/water-utilities/'],
  ['11', 'hwm_datagate', 'https://www.hwmglobal.com/datagate/'],
  ['12', 'ayyeka_dashboard_widgets', 'https://www.ayyeka.com/en/knowledge/dashboard-widgets'],

  // --- Przemysłowy monitoring aktywów i SCADA w chmurze ---
  ['13', 'ignition_quality_overlays', 'https://www.docs.inductiveautomation.com/docs/8.1/platform/tags/quality-codes-and-overlays'],
  ['14', 'ignition_quality_codes_table', 'https://www.docs.inductiveautomation.com/docs/8.1/platform/tags/quality-codes-and-overlays'],
  ['15', 'ignition_perspective_overview', 'https://www.docs.inductiveautomation.com/docs/8.1/ignition-modules/perspective'],
  ['16', 'ignition_perspective_mobile', 'https://inductiveautomation.com/ignition/modules/perspective'],
  ['17', 'ignition_responsive_tips', 'https://corsosystems.com/posts/5-responsive-design-tips-for-perspective'],
  ['18', 'hmi_best_practices', 'https://nfmconsulting.com/knowledge/hmi-design-best-practices/'],
  ['19', 'aveva_insight_dashboard', 'https://www.aveva.com/en/products/insight/'],
  ['20', 'aveva_insight_mobile', 'https://apps.apple.com/us/app/aveva-insight/id1428614248'],
  ['21', 'thingsboard_alarms_table', 'https://thingsboard.io/docs/pe/reference/widgets/alarm-widgets/alarms-table/'],
  ['22', 'thingsboard_alarms_filters', 'https://thingsboard.io/docs/pe/reference/widgets/alarm-widgets/alarms-table/'],
  ['23', 'thingsboard_alarm_rules', 'https://thingsboard.io/docs/user-guide/alarm-rules/'],
  ['24', 'thingsboard_working_with_alarms', 'https://thingsboard.io/docs/user-guide/alarms/'],
  ['25', 'thingsboard_claiming', 'https://thingsboard.io/docs/user-guide/claiming-devices/'],

  // --- Monitoring i obserwowalność IT ---
  ['26', 'grafana_nodata_error_states', 'https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rule-evaluation/nodata-and-error-states/'],
  ['27', 'grafana_missing_data', 'https://grafana.com/docs/grafana/latest/alerting/guides/missing-data/'],
  ['28', 'grafana_annotations', 'https://grafana.com/docs/grafana/latest/alerting/fundamentals/alert-rules/annotation-label/'],
  ['29', 'grafana_silences', 'https://grafana.com/docs/grafana/latest/alerting/configure-notifications/create-silence/'],
  ['30', 'grafana_alert_detail_redesign', 'https://grafana.com/blog/2024/05/14/grafana-alerting-new-tools-to-resolve-incidents-faster-and-avoid-alert-fatigue/'],
  ['31', 'grafana_active_notifications', 'https://grafana.com/docs/grafana/latest/alerting/monitor-status/view-active-notifications/'],
  ['32', 'zabbix_problems_list', 'https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/monitoring/problems'],
  ['33', 'zabbix_update_problem', 'https://www.zabbix.com/documentation/current/en/manual/acknowledgment'],
  ['34', 'zabbix_event_details', 'https://www.zabbix.com/documentation/current/en/manual/acknowledgment'],
  ['35', 'zabbix_suppression', 'https://www.zabbix.com/documentation/current/en/manual/acknowledgment/suppression'],
  ['36', 'zabbix_severity', 'https://www.zabbix.com/documentation/current/en/manual/config/triggers/severity'],
  ['37', 'alertmanager_overview', 'https://prometheus.io/docs/alerting/latest/alertmanager/'],
  ['38', 'alertmanager_inhibition', 'https://oneuptime.com/blog/post/2026-01-27-alertmanager-inhibition-rules/view'],
  ['39', 'datadog_monitor_status', 'https://docs.datadoghq.com/monitors/status/status_page/'],
  ['40', 'datadog_downtimes', 'https://docs.datadoghq.com/monitors/downtimes/'],

  // --- Wzorce mobilne, normy i wzorce ogólne ---
  ['41', 'pagerduty_mobile_incident', 'https://support.pagerduty.com/main/docs/mobile-app'],
  ['42', 'pagerduty_incidents_page', 'https://support.pagerduty.com/main/docs/navigate-the-incidents-page'],
  ['43', 'pagerduty_mobile_marketing', 'https://www.pagerduty.com/platform/incident-management/on-call-management/mobile/'],
  ['44', 'isa101_going_gray', 'https://control.com/technical-articles/going-gray/'],
  ['45', 'isa101_guide', 'https://hmilibrary.com/standards/isa-101'],
  ['46', 'opc_quality_codes', 'https://reference.opcfoundation.org/v104/Core/docs/Part8/A.4.3/'],
  ['47', 'wcag_141_examples', 'https://www.thewcag.com/criteria/1.4.1'],
  ['48', 'datacake_rule_engine', 'https://datacake.co/iot-rule-engine-lorawan-mqtt-sms-email-alerting'],
]

/** Numery ujęć są dwucyfrowe ('07'), więc --only 7 też ma trafiać. */
const padNum = (s) => String(s).trim().padStart(2, '0')

function positiveInt(raw, flag, fallback) {
  const value = Number(raw)
  if (!Number.isFinite(value) || value <= 0) {
    console.warn(`Zignorowano ${flag} ${raw} — oczekiwana liczba dodatnia; używam ${fallback}.`)
    return fallback
  }
  return value
}

function parseArgs(argv) {
  const args = { width: 1600, quality: 82, only: null, force: false }
  for (let i = 0; i < argv.length; i += 1) {
    const flag = argv[i]
    if (flag === '--force') args.force = true
    else if (flag === '--width') args.width = positiveInt(argv[++i], '--width', args.width)
    else if (flag === '--quality') args.quality = positiveInt(argv[++i], '--quality', args.quality)
    else if (flag === '--only') args.only = new Set(argv[++i].split(',').map(padNum))
  }
  return args
}

/** Zamyka typowe bannery zgód, żeby nie zasłaniały zrzutu. */
async function dismissConsent(page) {
  const selectors = [
    'button:has-text("Akceptuj")',
    'button:has-text("Zgadzam")',
    'button:has-text("Accept all")',
    'button:has-text("Accept All")',
    'button:has-text("I agree")',
    '#onetrust-accept-btn-handler',
    '[aria-label="Accept cookies"]',
  ]
  for (const selector of selectors) {
    try {
      const button = page.locator(selector).first()
      if (await button.isVisible({ timeout: 700 })) {
        await button.click({ timeout: 1500 })
        await page.waitForTimeout(400)
        return
      }
    } catch {
      // banner nie występuje na tej stronie — to normalne, idziemy dalej
    }
  }
}

async function capture(page, args, [num, slug, url], capturedUrls) {
  const target = join(OUT_DIR, `${num}_${slug}.webp`)
  if (!args.force && existsSync(target)) {
    // Także przy pominięciu rejestrujemy adres — inaczej po wznowieniu przerwanego
    // przebiegu bliźniacza pozycja zrobiłaby zrzut tej samej strony drugi raz.
    if (!capturedUrls.has(url)) capturedUrls.set(url, num)
    return { num, url, status: 'skipped' }
  }

  // Trzy pozycje na liście dzielą adres z wcześniejszą (README wyjaśnia, które):
  // jedna strona niesie dwa różne wzorce. Zrzut całej strony dałby dwa
  // identyczne pliki, więc drugiego nie robimy — trzeba go wykadrować ręcznie.
  const twin = capturedUrls.get(url)
  if (twin !== undefined) return { num, url, status: 'duplicate', twin }

  // Świadomie NIE 'networkidle': strony produktowe z analityką i czatem
  // potrafią nigdy nie osiągnąć bezczynności sieci i kończą się timeoutem
  // mimo poprawnie wyrenderowanej treści.
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45_000 })
  await dismissConsent(page)
  try {
    await page.waitForLoadState('networkidle', { timeout: 8_000 })
  } catch {
    // strona nadal coś dociąga — treść zwykle i tak jest już gotowa
  }
  await page.waitForTimeout(1200) // dociągnięcie obrazów ładowanych leniwie

  const raw = join(TMP_DIR, `${num}.png`)
  try {
    await page.screenshot({ path: raw, fullPage: true })
    await sharp(raw)
      .resize({ width: args.width, withoutEnlargement: true })
      .webp({ quality: args.quality })
      .toFile(target)
  } finally {
    await unlink(raw).catch(() => {})
  }

  capturedUrls.set(url, num)
  const { size } = await stat(target)
  return { num, url, status: 'ok', kb: Math.round(size / 1024) }
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  await mkdir(TMP_DIR, { recursive: true })

  const queue = args.only ? SHOTS.filter(([num]) => args.only.has(num)) : SHOTS
  const browser = await chromium.launch()
  const context = await browser.newContext({
    viewport: { width: args.width, height: 1200 },
    deviceScaleFactor: 1,
    locale: 'pl-PL',
  })
  const page = await context.newPage()

  const results = []
  const capturedUrls = new Map()
  const messages = {
    skipped: () => 'pominięto (plik istnieje)',
    duplicate: (r) => `ta sama strona co [${r.twin}] — wykadruj ręcznie`,
    ok: (r) => `${r.kb} KB`,
  }

  for (const shot of queue) {
    process.stdout.write(`[${shot[0]}] ${shot[1]} … `)
    try {
      const result = await capture(page, args, shot, capturedUrls)
      results.push(result)
      console.log(messages[result.status](result))
    } catch (error) {
      results.push({ num: shot[0], url: shot[2], status: 'error', message: error.message })
      console.log(`BŁĄD: ${error.message.split('\n')[0]}`)
    }
  }

  await browser.close()
  await rm(TMP_DIR, { recursive: true, force: true })

  const of = (status) => results.filter((r) => r.status === status)
  const ok = of('ok')
  const failed = of('error')
  const duplicates = of('duplicate')
  const oversized = ok.filter((r) => r.kb > 300)

  console.log(
    `\n— zebrano: ${ok.length}, pominięto: ${of('skipped').length}, ` +
      `do ręcznego kadrowania: ${duplicates.length}, błędów: ${failed.length}`,
  )
  if (oversized.length) {
    console.log(`— powyżej limitu 300 KB (obniż --quality albo --width): ${oversized.map((r) => r.num).join(', ')}`)
  }
  if (duplicates.length) {
    console.log('— dwa wzorce na jednej stronie; wykadruj drugi fragment ręcznie:')
    for (const d of duplicates) console.log(`   [${d.num}] źródło w pliku [${d.twin}] — ${d.url}`)
  }
  if (failed.length) {
    console.log('— nieudane, do zrobienia ręcznie (patrz README.md):')
    for (const f of failed) console.log(`   [${f.num}] ${f.url}`)
  }

  const files = (await readdir(OUT_DIR)).filter((f) => f.endsWith('.webp'))
  let total = 0
  for (const f of files) total += (await stat(join(OUT_DIR, f))).size
  console.log(`— katalog: ${files.length} plików, ${(total / 1024 / 1024).toFixed(1)} MB`)

  await writeFile(
    join(OUT_DIR, 'capture_log.json'),
    JSON.stringify({ capturedAt: new Date().toISOString(), args: { ...args, only: args.only && [...args.only] }, results }, null, 2),
  )
  console.log('— dziennik zapisany w capture_log.json (zawiera daty pobrania do wpisania w README.md)')
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
