import * as React from 'react';
import { cn } from '@/lib/cn';

interface ColumnDef<T> {
  key: keyof T | string;
  label: string;
  width?: string;
  render?: (row: T, index: number) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  isLoading?: boolean;
  isEmpty?: boolean;
  isError?: boolean;
  errorMessage?: string;
  emptyMessage?: string;
  onRowClick?: (row: T, index: number) => void;
  pageSize?: number;
  currentPage?: number;
  totalCount?: number;
  onPageChange?: (page: number) => void;
}

export function DataTable<T extends object>({
  columns,
  data,
  isLoading = false,
  isEmpty = false,
  isError = false,
  errorMessage = 'Błąd wczytywania danych',
  emptyMessage = 'Brak danych',
  onRowClick,
  pageSize = 20,
  currentPage = 1,
  totalCount,
  onPageChange,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-brand-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <p className="text-red-600 font-medium">{errorMessage}</p>
        </div>
      </div>
    );
  }

  // Ensure data is an array
  if (!Array.isArray(data)) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <p className="text-red-600 font-medium">Invalid data format: expected array</p>
          <p className="text-sm text-neutral-600 mt-2">Received: {typeof data}</p>
        </div>
      </div>
    );
  }

  if (isEmpty || data.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-neutral-500">{emptyMessage}</p>
      </div>
    );
  }

  const totalPages = totalCount ? Math.ceil(totalCount / pageSize) : 1;

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-neutral-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200 bg-neutral-50">
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  className="px-6 py-3 text-left text-sm font-semibold text-neutral-900"
                  style={{ width: col.width }}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={cn(
                  'border-b border-neutral-200',
                  onRowClick && 'cursor-pointer hover:bg-neutral-50'
                )}
                onClick={() => onRowClick?.(row, idx)}
              >
                {columns.map((col) => (
                  <td
                    key={`${idx}-${String(col.key)}`}
                    className="px-6 py-4 text-sm text-neutral-900"
                  >
                    {col.render
                      ? col.render(row, idx)
                      : String((row as Record<string, unknown>)[col.key as string] ?? '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-neutral-600">
            Strona {currentPage} z {totalPages}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange?.(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 rounded border border-neutral-300 text-sm font-medium hover:bg-neutral-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Poprzednia
            </button>
            <button
              onClick={() => onPageChange?.(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 rounded border border-neutral-300 text-sm font-medium hover:bg-neutral-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Następna
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
