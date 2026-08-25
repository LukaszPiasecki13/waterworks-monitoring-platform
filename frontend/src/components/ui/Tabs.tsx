import * as React from 'react';
import * as RadixTabs from '@radix-ui/react-tabs';
import { cn } from '@/lib/cn';

const Tabs = RadixTabs.Root;

type TabsListProps = React.ComponentPropsWithoutRef<typeof RadixTabs.List> & {
  variant?: 'pill' | 'underline';
};

const TabsList = React.forwardRef<
  React.ElementRef<typeof RadixTabs.List>,
  TabsListProps
>(({ className, variant = 'pill', ...props }, ref) => (
  <RadixTabs.List
    ref={ref}
    className={cn(
      variant === 'pill'
        ? 'inline-flex h-10 items-center justify-center rounded-md border border-neutral-200 bg-neutral-100 p-1'
        : 'inline-flex items-center gap-6 border-0 bg-transparent p-0 h-auto',
      className
    )}
    {...props}
  />
));

TabsList.displayName = 'TabsList';

type TabsTriggerProps = React.ComponentPropsWithoutRef<typeof RadixTabs.Trigger> & {
  variant?: 'pill' | 'underline';
};

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof RadixTabs.Trigger>,
  TabsTriggerProps
>(({ className, variant = 'pill', ...props }, ref) => (
  <RadixTabs.Trigger
    ref={ref}
    className={cn(
      'transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500',
      'disabled:pointer-events-none disabled:opacity-50',
      variant === 'pill'
        ? [
            'inline-flex items-center justify-center whitespace-nowrap rounded px-3 py-1.5 text-sm font-medium',
            'data-[state=active]:bg-surface data-[state=active]:text-neutral-900 data-[state=active]:shadow-sm',
            'data-[state=inactive]:text-neutral-600 data-[state=inactive]:hover:text-neutral-900',
          ]
        : [
            'inline-flex items-center whitespace-nowrap rounded-none border-b-2 border-transparent px-0 py-3 text-sm font-medium text-neutral-600',
            'data-[state=active]:border-brand-500 data-[state=active]:text-neutral-900 data-[state=active]:bg-transparent data-[state=active]:shadow-none',
            'data-[state=inactive]:hover:text-neutral-900',
          ],
      className
    )}
    {...props}
  />
));

TabsTrigger.displayName = 'TabsTrigger';

type TabsContentProps = React.ComponentPropsWithoutRef<typeof RadixTabs.Content>;

const TabsContent = React.forwardRef<
  React.ElementRef<typeof RadixTabs.Content>,
  TabsContentProps
>(({ className, ...props }, ref) => (
  <RadixTabs.Content
    ref={ref}
    className={cn('mt-2 ring-offset-surface focus-visible:outline-none', className)}
    {...props}
  />
));

TabsContent.displayName = 'TabsContent';

export { Tabs, TabsList, TabsTrigger, TabsContent };
