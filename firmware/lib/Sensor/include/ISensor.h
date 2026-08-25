#pragma once

class ISensor {
 public:
  virtual ~ISensor() = default;

  // Initialize sensor. Return true if successful.
  virtual bool init() = 0;

  // Read sensor value. Return true if successful, false if error.
  // outValue is filled only if return is true.
  virtual bool read(float& outValue) = 0;

  // Get the sensor's log tag (e.g., "[PT100]")
  virtual const char* getTag() const = 0;
};
