import { useState } from 'react';
import { Input } from '@/components/ui/Input';

interface DeviceFilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  isActive: boolean | null;
  onIsActiveChange: (value: boolean | null) => void;
  credentialStatus: string | null;
  onCredentialStatusChange: (value: string | null) => void;
  assigned: string | null;
  onAssignedChange: (value: string | null) => void;
}

export function DeviceFilterBar({
  search,
  onSearchChange,
  isActive,
  onIsActiveChange,
  credentialStatus,
  onCredentialStatusChange,
  assigned,
  onAssignedChange,
}: DeviceFilterBarProps) {
  const [searchTimeout, setSearchTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);

  const handleSearchChange = (value: string) => {
    onSearchChange(value);
    if (searchTimeout) clearTimeout(searchTimeout);
    setSearchTimeout(setTimeout(() => {}, 300));
  };

  return (
    <div className="bg-white border-b border-neutral-200 p-4">
      <div className="grid grid-cols-4 gap-4">
        <div>
          <label className="block text-sm text-neutral-600 mb-2">Wyszukaj</label>
          <Input
            placeholder="WW-7F2A19C0 lub nazwa..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full"
          />
        </div>
        <div>
          <label className="block text-sm text-neutral-600 mb-2">Aktywność</label>
          <select
            value={isActive === null ? '' : isActive ? 'true' : 'false'}
            onChange={(e) => {
              if (e.target.value === '') onIsActiveChange(null);
              else onIsActiveChange(e.target.value === 'true');
            }}
            className="w-full px-3 py-2 border border-neutral-300 rounded-md bg-white text-sm"
          >
            <option value="">— wszystkie —</option>
            <option value="true">Aktywne</option>
            <option value="false">Nieaktywne</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-neutral-600 mb-2">Przypisanie</label>
          <select
            value={assigned ?? ''}
            onChange={(e) => onAssignedChange(e.target.value || null)}
            className="w-full px-3 py-2 border border-neutral-300 rounded-md bg-white text-sm"
          >
            <option value="">— wszystkie —</option>
            <option value="assigned">Przypisane</option>
            <option value="unassigned">Nieprzypisane</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-neutral-600 mb-2">Poświadczenie</label>
          <select
            value={credentialStatus ?? ''}
            onChange={(e) => onCredentialStatusChange(e.target.value || null)}
            className="w-full px-3 py-2 border border-neutral-300 rounded-md bg-white text-sm"
          >
            <option value="">— wszystkie —</option>
            <option value="claimed">Claimed</option>
            <option value="unclaimed">Unclaimed</option>
            <option value="revoked">Revoked</option>
          </select>
        </div>
      </div>
    </div>
  );
}
