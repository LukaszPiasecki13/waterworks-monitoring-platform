import React from 'react';
import { cn } from '@/lib/cn';
import type { SettingsSection } from './settingsConfig';

interface SettingsRailProps {
  sections: SettingsSection[];
  activeSection: string;
  onSelectSection: (sectionKey: string) => void;
}

const SettingsRail = React.forwardRef<HTMLDivElement, SettingsRailProps>(
  ({ sections, activeSection, onSelectSection }, ref) => (
    <div
      ref={ref}
      className="w-40 flex-none border-r border-neutral-200 bg-neutral-50 flex flex-col gap-1 p-3"
    >
      {sections.map((section) => {
        const Icon = section.icon;
        return (
          <button
            key={section.key}
            onClick={() => onSelectSection(section.key)}
            role="tab"
            aria-selected={activeSection === section.key}
            className={cn(
              'text-left text-sm font-medium px-3 py-2.5 rounded-md transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500',
              'border-l-2 flex items-center gap-2',
              activeSection === section.key
                ? 'bg-brand-50 text-brand-700 border-l-brand-500 font-semibold'
                : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 border-l-transparent'
            )}
          >
            {Icon && <Icon className="h-4 w-4 flex-shrink-0" />}
            <span>{section.label}</span>
          </button>
        );
      })}
    </div>
  )
);

SettingsRail.displayName = 'SettingsRail';

export { SettingsRail };
