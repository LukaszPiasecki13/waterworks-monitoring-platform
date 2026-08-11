import { Menu } from 'lucide-react';
import { OrganizationSwitcher } from './OrganizationSwitcher';

interface TopbarProps {
  onMenuClick?: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {

  return (
    <header className="sticky top-0 z-40 bg-surface border-b border-neutral-200 shadow-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="inline-flex items-center justify-center lg:hidden p-2 rounded-lg text-neutral-700 hover:bg-neutral-100"
            aria-label="Toggle menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-xl font-semibold text-neutral-900">Waterworks Monitor</h1>
            <p className="text-xs text-neutral-500">Panel monitorowania sieci wodociągów</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <OrganizationSwitcher />
        </div>
      </div>
    </header>
  );
}
