import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogBody, DialogFooter } from '@/components/ui/Dialog';
import { Copy, Eye, EyeOff } from 'lucide-react';
import { toast } from '@/components/ui/Toast';
import { cn } from '@/lib/cn';

interface DeviceSecretRevealDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  deviceId?: string | null;
  secret?: string | null;
}

export function DeviceSecretRevealDialog({
  open,
  onOpenChange,
  deviceId,
  secret = null,
}: DeviceSecretRevealDialogProps) {
  const [isRevealed, setIsRevealed] = useState(false);

  const handleCopySecret = () => {
    if (secret) {
      navigator.clipboard.writeText(secret);
      toast.success('Sekret skopiowany do schowka');
    }
  };

  const handleCopyDeviceId = () => {
    if (deviceId) {
      navigator.clipboard.writeText(deviceId);
      toast.success('ID urządzenia skopiowane do schowka');
    }
  };

  const maskedSecret = secret ? '•'.repeat(secret.length) : '—';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Sekret urządzenia</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <div className="space-y-4">
            <div>
              <p className="mb-2 text-sm font-medium text-neutral-900">ID urządzenia</p>
              <div className="flex gap-2">
                <code className="flex-1 rounded bg-neutral-100 px-3 py-2 text-sm font-mono text-neutral-900">
                  {deviceId || '—'}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyDeviceId}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <p className="text-sm font-medium text-neutral-900">Sekret dostępu</p>
                {secret && (
                  <button
                    onClick={() => setIsRevealed(!isRevealed)}
                    className="text-xs text-teal-600 hover:text-teal-700 flex items-center gap-1"
                  >
                    {isRevealed ? (
                      <>
                        <EyeOff className="h-4 w-4" />
                        Ukryj
                      </>
                    ) : (
                      <>
                        <Eye className="h-4 w-4" />
                        Pokaż
                      </>
                    )}
                  </button>
                )}
              </div>
              {secret ? (
                <div className="flex gap-2">
                  <code className={cn(
                    'flex-1 rounded px-3 py-2 text-sm font-mono',
                    isRevealed
                      ? 'bg-neutral-100 text-neutral-900'
                      : 'bg-red-50 text-red-600'
                  )}>
                    {isRevealed ? secret : maskedSecret}
                  </code>
                  {isRevealed && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopySecret}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ) : (
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                  <p className="text-sm text-gray-600">
                    Sekret nie jest dostępny. Sekrety pokazywane są tylko po utworzeniu urządzenia.
                  </p>
                </div>
              )}
            </div>

            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
              <p className="text-xs text-amber-800">
                <strong>Uwaga:</strong> Zachowaj sekret w bezpiecznym miejscu. Nie będziesz mógł go ponownie wyświetlić.
              </p>
            </div>
          </div>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange?.(false)}>
            Zamknij
          </Button>
          <Button onClick={() => onOpenChange?.(false)}>
            Zrozumiano
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
