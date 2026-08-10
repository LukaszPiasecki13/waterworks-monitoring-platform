import * as React from 'react';
import { cn } from '@/lib/cn';
import {
  OBJECT_STATUS_LABEL_MAP,
  DATA_QUALITY_LABEL_MAP,
  SEMANTIC_STATUS_TO_TAILWIND,
  SEMANTIC_STATUS_TO_DOT_COLOR,
  getObjectStatusColor,
  getDataQualityColor,
  type ObjectStatus,
  type DataQuality,
} from '@/lib/statusConfig';

interface StatusPillProps extends React.HTMLAttributes<HTMLDivElement> {
  kind: 'objectStatus' | 'quality';
  value: ObjectStatus | DataQuality;
}

const StatusPill = React.forwardRef<HTMLDivElement, StatusPillProps>(
  ({ className, kind, value, ...props }, ref) => {
    const isObjectStatus = kind === 'objectStatus';
    const label = isObjectStatus
      ? OBJECT_STATUS_LABEL_MAP[value as ObjectStatus]
      : DATA_QUALITY_LABEL_MAP[value as DataQuality];

    const semanticStatus = isObjectStatus
      ? getObjectStatusColor(value as ObjectStatus)
      : getDataQualityColor(value as DataQuality);

    const bgStyles = SEMANTIC_STATUS_TO_TAILWIND[semanticStatus];
    const dotColor = SEMANTIC_STATUS_TO_DOT_COLOR[semanticStatus];

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border',
          bgStyles,
          className
        )}
        {...props}
      >
        <span className={cn('text-lg leading-none', dotColor)}>●</span>
        <span>{label}</span>
      </div>
    );
  }
);

StatusPill.displayName = 'StatusPill';

export { StatusPill };
