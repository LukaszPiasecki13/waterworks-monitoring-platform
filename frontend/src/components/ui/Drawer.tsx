import * as React from 'react';
import * as RadixDialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';

interface DrawerProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

const Drawer = ({ open, onOpenChange, children }: DrawerProps) => (
  <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
    {children}
  </RadixDialog.Root>
);

type DrawerTriggerProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

const DrawerTrigger = React.forwardRef<HTMLButtonElement, DrawerTriggerProps>(
  ({ ...props }, ref) => <RadixDialog.Trigger ref={ref} {...props} />
);

DrawerTrigger.displayName = 'DrawerTrigger';

const DrawerContent = React.forwardRef<
  React.ElementRef<typeof RadixDialog.Content>,
  React.ComponentPropsWithoutRef<typeof RadixDialog.Content>
>(({ className, ...props }, ref) => (
  <RadixDialog.Portal>
    <RadixDialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
    <RadixDialog.Content
      ref={ref}
      className={cn(
        'fixed right-0 top-0 z-50 h-full w-full max-w-md overflow-y-auto',
        'bg-white shadow-lg p-6',
        'data-[state=open]:animate-in data-[state=open]:slide-in-from-right',
        'data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right',
        'focus-visible:outline-none',
        className
      )}
      {...props}
    />
  </RadixDialog.Portal>
));

DrawerContent.displayName = 'DrawerContent';

type DrawerHeaderProps = React.HTMLAttributes<HTMLDivElement>;

const DrawerHeader = React.forwardRef<HTMLDivElement, DrawerHeaderProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center justify-between mb-6', className)} {...props} />
  )
);

DrawerHeader.displayName = 'DrawerHeader';

type DrawerTitleProps = React.ComponentPropsWithoutRef<typeof RadixDialog.Title>;

const DrawerTitle = React.forwardRef<
  React.ElementRef<typeof RadixDialog.Title>,
  DrawerTitleProps
>(({ className, ...props }, ref) => (
  <RadixDialog.Title
    ref={ref}
    className={cn('text-lg font-semibold text-neutral-900', className)}
    {...props}
  />
));

DrawerTitle.displayName = 'DrawerTitle';

type DrawerCloseProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

const DrawerClose = React.forwardRef<HTMLButtonElement, DrawerCloseProps>(
  ({ className, ...props }, ref) => (
    <RadixDialog.Close
      ref={ref}
      className={cn(
        'rounded p-1 hover:bg-neutral-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500',
        className
      )}
      {...props}
    >
      <X className="h-5 w-5" />
    </RadixDialog.Close>
  )
);

DrawerClose.displayName = 'DrawerClose';

type DrawerBodyProps = React.HTMLAttributes<HTMLDivElement>;

const DrawerBody = React.forwardRef<HTMLDivElement, DrawerBodyProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('space-y-6', className)} {...props} />
  )
);

DrawerBody.displayName = 'DrawerBody';

export {
  Drawer,
  DrawerTrigger,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerClose,
  DrawerBody,
};
