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
  fieldErrors?: Record<string, string>;
  conflictMessage?: string;
}

export function parseApiError(error: unknown): ParsedApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data as any;

    /* 409 Conflict */
    if (status === 409) {
      return {
        message: typeof data.detail === 'string' ? data.detail : 'Conflict',
        statusCode: 409,
        conflictMessage: typeof data.detail === 'string' ? data.detail : undefined,
      };
    }

    /* 422 Unprocessable Entity (Pydantic validation) */
    if (status === 422) {
      const fieldErrors: Record<string, string> = {};
      let messages: string[] = [];

      if (Array.isArray(data.detail)) {
        data.detail.forEach((err: ApiErrorDetail) => {
          if (err.loc && err.loc.length > 0) {
            const fieldName = err.loc[err.loc.length - 1];
            fieldErrors[String(fieldName)] = err.msg || 'Invalid value';
          }
          if (err.msg) {
            messages.push(err.msg);
          }
        });
      }

      return {
        message: messages.length > 0 ? messages.join('; ') : 'Validation error',
        statusCode: 422,
        fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
      };
    }

    /* Generic error */
    return {
      message: typeof data.detail === 'string' ? data.detail : 'An error occurred',
      statusCode: status,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }

  return {
    message: 'Unknown error occurred',
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
