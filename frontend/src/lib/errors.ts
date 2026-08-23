import axios from 'axios';

export class SessionChangedError extends Error {
  constructor(message = 'Session changed during operation') {
    super(message);
    this.name = 'SessionChangedError';
  }
}

export interface ApiErrorDetail {
  loc?: string[];
  msg?: string;
  type?: string;
}

export interface ParsedApiError {
  message: string;
  statusCode?: number;
  code?: string;
  fieldErrors?: Record<string, string>;
  conflictMessage?: string;
}

interface ApiErrorResponseData {
  detail?: string | ApiErrorDetail[];
}

export function parseApiError(error: unknown): ParsedApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data as ApiErrorResponseData & { code?: string };
    const code = data?.code;

    const domainErrorMessages: Record<string, string> = {
      ACTIVATION_CODE_NOT_FOUND: 'Kod aktywacyjny nie został znaleziony',
      ACTIVATION_CODE_EXPIRED: 'Kod aktywacyjny wygasł',
      ACTIVATION_CODE_CANCELLED: 'Kod aktywacyjny został anulowany',
      ACTIVATION_CODE_ALREADY_USED: 'Kod aktywacyjny został już użyty przez inne urządzenie',
      DEVICE_ALREADY_REGISTERED: 'Urządzenie o tym numerze seryjnym jest już zarejestrowane',
      DEVICE_NOT_FOUND: 'Urządzenie nie zostało znalezione lub nie ukończyło aktywacji',
    };

    /* 409 Conflict */
    if (status === 409) {
      const message = code && domainErrorMessages[code] ? domainErrorMessages[code] : (typeof data.detail === 'string' ? data.detail : 'Konflikt');
      return {
        message,
        statusCode: 409,
        code,
        conflictMessage: message,
      };
    }

    /* 410 Gone */
    if (status === 410) {
      const message = code && domainErrorMessages[code] ? domainErrorMessages[code] : (typeof data.detail === 'string' ? data.detail : 'Zasób nie jest dostępny');
      return {
        message,
        statusCode: 410,
        code,
      };
    }

    /* 404 Not Found */
    if (status === 404) {
      const message = code && domainErrorMessages[code] ? domainErrorMessages[code] : (typeof data.detail === 'string' ? data.detail : 'Nie znaleziono');
      return {
        message,
        statusCode: 404,
        code,
      };
    }

    /* 422 Unprocessable Entity (Pydantic validation) */
    if (status === 422) {
      const fieldErrors: Record<string, string> = {};
      const messages: string[] = [];

      if (Array.isArray(data.detail)) {
        data.detail.forEach((err: ApiErrorDetail) => {
          if (err.loc && err.loc.length > 0) {
            const fieldName = err.loc[err.loc.length - 1];
            fieldErrors[String(fieldName)] = err.msg || 'Nieprawidłowa wartość';
          }
          if (err.msg) {
            messages.push(err.msg);
          }
        });
      }

      return {
        message: messages.length > 0 ? messages.join('; ') : 'Błąd walidacji',
        statusCode: 422,
        code,
        fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
      };
    }

    /* Generic error */
    return {
      message: typeof data.detail === 'string' ? data.detail : 'Wystąpił błąd',
      statusCode: status,
      code,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }

  return {
    message: 'Nieznany błąd',
  };
}

export function applyServerErrors(
  error: ParsedApiError,
  setError: (field: string, message: string) => void
): void {
  if (error.fieldErrors) {
    Object.entries(error.fieldErrors).forEach(([field, message]) => {
      setError(field, message);
    });
  }
}
