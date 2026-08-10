import * as React from 'react';
import { cn } from '@/lib/cn';

interface FormFieldProps extends React.HTMLAttributes<HTMLDivElement> {
  label?: string;
  description?: string;
  error?: string;
  required?: boolean;
}

const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ className, label, description, error, required, children, ...props }, ref) => (
    <div ref={ref} className={cn('space-y-2', className)} {...props}>
      {label && (
        <label className="text-sm font-medium text-neutral-900">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      {children}
      {description && <p className="text-xs text-neutral-500">{description}</p>}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
);

FormField.displayName = 'FormField';

export { FormField };
