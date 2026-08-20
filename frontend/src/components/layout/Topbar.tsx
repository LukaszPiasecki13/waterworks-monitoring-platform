import { Menu, ChevronLeft, ChevronRight } from 'lucide-react';
import { EnvironmentSwitcher } from './EnvironmentSwitcher';

interface TopbarProps {
  onMenuClick?: () => void;
  collapsed?: boolean;
  onToggleSidebar?: () => void;
}

export function Topbar({ onMenuClick, collapsed = false, onToggleSidebar }: TopbarProps) {

  return (
    <header className="sticky top-0 z-40 bg-surface border-b border-neutral-200 shadow-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <button
            onClick={onMenuClick}
            className="inline-flex items-center justify-center lg:hidden p-2 rounded-lg text-neutral-700 hover:bg-neutral-100"
            aria-label="Toggle menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <button
            onClick={onToggleSidebar}
            className="hidden lg:inline-flex items-center justify-center p-2 rounded-lg text-neutral-700 hover:bg-neutral-100"
            aria-label={collapsed ? 'Rozwiń pasek boczny' : 'Zwiń pasek boczny'}
            title={collapsed ? 'Rozwiń pasek boczny' : 'Zwiń pasek boczny'}
          >
            {collapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
          </button>
          <div>
            <h1 className="text-xl font-semibold text-neutral-900">Waterworks Monitor</h1>
            <p className="text-xs text-neutral-500">Panel monitorowania sieci wodociągów</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <EnvironmentSwitcher />
        </div>
      </div>
    </header>
  );
}
