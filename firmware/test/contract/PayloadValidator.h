#pragma once
//
// Walidator pakietu telemetrycznego względem kontraktu backendu.
//
// Sprawdza dokładnie to, co odrzuciłby pydantic po stronie backendu:
// obecność i nadmiarowość kluczy, dopuszczalne wartości i zakresy. Reguły
// pochodzą z generowanego PayloadContract.h; kody błędów — z SensorRegistry.h.
//
// Walidator jest kodem testowym, nie firmware'owym: żyje w test/contract/
// i nie trafia do binarki urządzenia.
//
#include <ArduinoJson.h>
#include <PayloadContract.h>
#include <SensorRegistry.h>

#include <cstring>
#include <string>
#include <vector>

namespace payload_contract {

struct Violation {
  std::string path;     // np. "windows[0].points[1].quality"
  std::string message;  // dlaczego backend by to odrzucił
};

class Validator {
 public:
  // Zwraca listę naruszeń; pusta lista = backend przyjąłby ten pakiet.
  static std::vector<Violation> validate(JsonDocument& doc) {
    Validator validator;
    validator.checkPacket(doc);
    return validator.violations_;
  }

  static std::string describe(const std::vector<Violation>& violations) {
    std::string out;
    for (const Violation& v : violations) {
      out += "\n  - " + v.path + ": " + v.message;
    }
    return out;
  }

 private:
  std::vector<Violation> violations_;

  void fail(const std::string& path, const std::string& message) { violations_.push_back({path, message}); }

  static bool contains(const char* const* list, size_t count, const std::string& value) {
    for (size_t i = 0; i < count; ++i) {
      if (list[i] && value == list[i]) return true;
    }
    return false;
  }

  // Zbiera klucze obiektu przez publiczne API ArduinoJson (JsonPair), a nie
  // przez rozszerzenia konkretnej implementacji.
  static std::vector<std::string> keysOf(JsonObject obj) {
    std::vector<std::string> keys;
    for (JsonPair entry : obj) {
      keys.push_back(std::string(entry.key().c_str()));
    }
    return keys;
  }

  void checkKeys(const std::string& path, const std::vector<std::string>& present, const char* const* required,
                 size_t requiredCount, const char* const* optional, size_t optionalCount) {
    for (size_t i = 0; i < requiredCount; ++i) {
      if (!required[i]) continue;
      bool found = false;
      for (const std::string& key : present) {
        if (key == required[i]) {
          found = true;
          break;
        }
      }
      if (!found) fail(path, std::string("brak wymaganego klucza '") + required[i] + "'");
    }

    if (!PayloadContract::FORBIDS_EXTRA_KEYS) return;
    for (const std::string& key : present) {
      if (contains(required, requiredCount, key)) continue;
      if (contains(optional, optionalCount, key)) continue;
      fail(path, "nadmiarowy klucz '" + key + "' (backend ma extra=forbid)");
    }
  }

  // Backend parsuje sent_at/window_start jako datetime; pusty łańcuch albo
  // znacznik bez strefy zostałyby odrzucone.
  void checkIso8601(const std::string& path, JsonVariant value) {
    const char* text = value.as<const char*>();
    if (!text) {
      fail(path, "oczekiwano znacznika czasu jako łańcucha znaków");
      return;
    }
    std::string stamp(text);
    if (stamp.empty()) {
      fail(path, "pusty znacznik czasu");
      return;
    }
    if (stamp.size() < 20 || stamp[4] != '-' || stamp[7] != '-' || stamp[10] != 'T' || stamp.back() != 'Z') {
      fail(path, "znacznik '" + stamp + "' nie ma formatu YYYY-MM-DDTHH:MM:SS[.sss]Z");
      return;
    }
    if (stamp.rfind("1970-", 0) == 0) {
      fail(path, "znacznik z 1970 roku — czas liczony od startu urządzenia zamiast UTC");
    }
  }

  void checkPacket(JsonDocument& doc) {
    JsonObject root = doc.as<JsonObject>();
    if (root.isNull()) {
      fail("$", "pakiet nie jest obiektem JSON");
      return;
    }

    checkKeys("$", keysOf(root), PayloadContract::PACKET_REQUIRED, PayloadContract::PACKET_REQUIRED_COUNT,
              PayloadContract::PACKET_OPTIONAL, PayloadContract::PACKET_OPTIONAL_COUNT);

    if (!doc["v"].isNull()) {
      int version = doc["v"].as<int>();
      if (version < PayloadContract::V_MIN || version > PayloadContract::V_MAX) {
        fail("$.v", "wersja " + std::to_string(version) + " poza zakresem akceptowanym przez backend");
      }
    }

    if (!doc["device_id"].isNull()) {
      const char* deviceId = doc["device_id"].as<const char*>();
      if (!deviceId || std::strlen(deviceId) == 0) {
        fail("$.device_id", "device_id musi być niepustym łańcuchem");
      } else if (std::strlen(deviceId) > PayloadContract::DEVICE_ID_MAX_LENGTH) {
        fail("$.device_id", "device_id dłuższy niż limit backendu");
      }
    }

    if (!doc["sent_at"].isNull()) checkIso8601("$.sent_at", doc["sent_at"]);

    JsonArray windows = doc["windows"].as<JsonArray>();
    if (windows.isNull()) {
      fail("$.windows", "windows musi być tablicą");
    } else {
      if (windows.size() < PayloadContract::MIN_WINDOWS) {
        fail("$.windows", "pakiet musi zawierać co najmniej " + std::to_string(PayloadContract::MIN_WINDOWS) +
                              " okno pomiarowe");
      }
      for (size_t i = 0; i < windows.size(); ++i) {
        checkWindow("$.windows[" + std::to_string(i) + "]", windows[i]);
      }
    }

    if (!doc["errors"].isNull()) {
      JsonArray errors = doc["errors"].as<JsonArray>();
      if (errors.isNull()) {
        fail("$.errors", "errors musi być tablicą");
      } else {
        for (size_t i = 0; i < errors.size(); ++i) {
          checkError("$.errors[" + std::to_string(i) + "]", errors[i]);
        }
      }
    }
  }

  void checkWindow(const std::string& path, JsonVariant window) {
    JsonObject obj = window.as<JsonObject>();
    if (obj.isNull()) {
      fail(path, "okno musi być obiektem");
      return;
    }

    checkKeys(path, keysOf(obj), PayloadContract::WINDOW_REQUIRED, PayloadContract::WINDOW_REQUIRED_COUNT,
              PayloadContract::WINDOW_OPTIONAL, PayloadContract::WINDOW_OPTIONAL_COUNT);

    if (!window["window_start"].isNull()) checkIso8601(path + ".window_start", window["window_start"]);

    if (!window["window_seconds"].isNull()) {
      int seconds = window["window_seconds"].as<int>();
      if (seconds <= PayloadContract::WINDOW_SECONDS_MIN_EXCLUSIVE || seconds > PayloadContract::WINDOW_SECONDS_MAX) {
        fail(path + ".window_seconds", "wartość " + std::to_string(seconds) + " poza zakresem backendu");
      }
    }

    JsonArray points = window["points"].as<JsonArray>();
    if (points.isNull()) {
      fail(path + ".points", "points musi być tablicą");
      return;
    }
    for (size_t i = 0; i < points.size(); ++i) {
      checkPoint(path + ".points[" + std::to_string(i) + "]", points[i]);
    }
  }

  void checkPoint(const std::string& path, JsonVariant point) {
    JsonObject obj = point.as<JsonObject>();
    if (obj.isNull()) {
      fail(path, "punkt musi być obiektem");
      return;
    }

    checkKeys(path, keysOf(obj), PayloadContract::POINT_REQUIRED, PayloadContract::POINT_REQUIRED_COUNT,
              PayloadContract::POINT_OPTIONAL, PayloadContract::POINT_OPTIONAL_COUNT);

    const char* pointId = point["point_id"].as<const char*>();
    if (!pointId || std::strlen(pointId) == 0) {
      fail(path + ".point_id", "point_id musi być niepustym łańcuchem");
    } else if (std::strlen(pointId) > PayloadContract::POINT_ID_MAX_LENGTH) {
      fail(path + ".point_id", "point_id dłuższy niż limit backendu");
    }

    const char* type = point["type"].as<const char*>();
    if (!type || std::strlen(type) == 0) {
      fail(path + ".type", "type musi być niepustym łańcuchem");
    } else if (!SensorRegistry::isValidPointType(type)) {
      fail(path + ".type", std::string("typ punktu '") + type + "' spoza rejestru czujników");
    }

    const char* unit = point["unit"].as<const char*>();
    if (!unit || std::strlen(unit) == 0) fail(path + ".unit", "unit musi być niepustym łańcuchem");

    const char* quality = point["quality"].as<const char*>();
    if (!quality || std::strlen(quality) == 0) fail(path + ".quality", "quality musi być niepustym łańcuchem");

    if (PayloadContract::POINT_REQUIRES_VALUE_OR_AGGREGATE) {
      bool hasValue = !point["value"].isNull();
      bool hasAggregate = false;
      for (size_t i = 0; i < PayloadContract::POINT_AGGREGATES_COUNT; ++i) {
        const char* name = PayloadContract::POINT_AGGREGATES[i];
        if (name && !point[name].isNull()) hasAggregate = true;
      }
      if (!hasValue && !hasAggregate) {
        fail(path, "punkt nie niesie ani value, ani żadnego agregatu (avg/min/max)");
      }
    }
  }

  void checkError(const std::string& path, JsonVariant error) {
    JsonObject obj = error.as<JsonObject>();
    if (obj.isNull()) {
      fail(path, "wpis błędu musi być obiektem");
      return;
    }

    checkKeys(path, keysOf(obj), PayloadContract::ERROR_REQUIRED, PayloadContract::ERROR_REQUIRED_COUNT,
              PayloadContract::ERROR_OPTIONAL, PayloadContract::ERROR_OPTIONAL_COUNT);

    const char* code = error["code"].as<const char*>();
    if (!code || std::strlen(code) == 0) {
      fail(path + ".code", "code musi być niepustym łańcuchem");
    } else if (!SensorRegistry::isValidErrorCode(code)) {
      // Backend waliduje kod rejestrem i odrzuca CAŁY pakiet, nie sam wpis.
      fail(path + ".code", std::string("kod '") + code + "' spoza rejestru — backend odrzuci cały pakiet");
    }

    const char* severity = error["severity"].as<const char*>();
    if (!severity) {
      fail(path + ".severity", "severity musi być łańcuchem");
    } else if (!contains(PayloadContract::ERROR_SEVERITIES, PayloadContract::ERROR_SEVERITIES_COUNT,
                         std::string(severity))) {
      fail(path + ".severity", std::string("poziom '") + severity + "' spoza Literal akceptowanego przez backend");
    } else if (code && SensorRegistry::isValidErrorCode(code)) {
      const char* expected = SensorRegistry::severityForErrorCode(code);
      if (expected && std::strcmp(expected, severity) != 0) {
        fail(path + ".severity", std::string("poziom '") + severity + "' nie zgadza się z rejestrem ('" + expected +
                                     "') dla kodu " + code);
      }
    }

    if (!error["message"].isNull()) {
      const char* message = error["message"].as<const char*>();
      if (message && std::strlen(message) > PayloadContract::ERROR_MESSAGE_MAX_LENGTH) {
        fail(path + ".message", "message dłuższy niż limit backendu");
      }
    }

    if (!error["point_id"].isNull()) {
      const char* pointId = error["point_id"].as<const char*>();
      if (pointId && std::strlen(pointId) > PayloadContract::POINT_ID_MAX_LENGTH) {
        fail(path + ".point_id", "point_id dłuższy niż limit backendu");
      }
    }
  }
};

}  // namespace payload_contract
