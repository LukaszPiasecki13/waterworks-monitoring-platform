import { useState } from 'react';
import { useActivationCodes, useCreateActivationCode, useCancelActivationCode } from '@/hooks/useActivationCodes';
import { useActivePermissions } from '@/hooks/useActivePermissions';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/Dialog';
import { Plus, Trash2, Copy, Check } from 'lucide-react';
import { toast } from '@/components/ui/Toast';
import type { ActivationCode } from '@/types/coreData';

export function PlatformActivationCodesPage() {
  const { data: response = { items: [], total: 0 }, isLoading } = useActivationCodes();
  const codes = response.items || [];
  const createMutation = useCreateActivationCode();
  const cancelMutation = useCancelActivationCode();
  const { hasPermission } = useActivePermissions();
  const canManage = hasPermission('PLATFORM_MANAGE_DEVICE_PROVISIONING');

  const [showCodeDialog, setShowCodeDialog] = useState(false);
  const [generatedCode, setGeneratedCode] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const handleGenerateCode = async () => {
    try {
      const result = await createMutation.mutateAsync();
      setGeneratedCode(result.activation_code);
      setShowCodeDialog(true);
    } catch {
      toast.error('Błąd przy generowaniu kodu');
    }
  };

  const handleCopyCode = () => {
    if (generatedCode) {
      navigator.clipboard.writeText(generatedCode);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleCloseCodeDialog = () => {
    setShowCodeDialog(false);
    setGeneratedCode(null);
    setCopySuccess(false);
  };

  const handleDeleteClick = (id: string) => {
    setDeleteId(id);
  };

  const handleConfirmDelete = async () => {
    if (!deleteId) return;
    try {
      await cancelMutation.mutateAsync(deleteId);
      toast.success('Kod anulowany');
      setDeleteId(null);
    } catch {
      toast.error('Błąd przy anulowaniu kodu');
    }
  };

  const columns = [
    {
      key: 'id',
      label: 'ID',
      render: (row: ActivationCode) => row.id.slice(0, 8) + '...',
    },
    {
      key: 'status',
      label: 'Status',
      render: (row: ActivationCode) => {
        const statusColors: Record<string, string> = {
          unused: 'bg-blue-100 text-blue-800',
          used: 'bg-green-100 text-green-800',
          expired: 'bg-gray-100 text-gray-800',
          cancelled: 'bg-red-100 text-red-800',
        };
        return (
          <span className={`px-2 py-1 rounded text-sm font-medium ${statusColors[row.status] || ''}`}>
            {row.status}
          </span>
        );
      },
    },
    {
      key: 'serial_number',
      label: 'Numer seryjny',
      render: (row: ActivationCode) => row.serial_number || '—',
    },
    {
      key: 'expires_at',
      label: 'Wygasa',
      render: (row: ActivationCode) => {
        const date = new Date(row.expires_at);
        return date.toLocaleString('pl-PL');
      },
    },
    {
      key: 'actions',
      label: 'Akcje',
      render: (row: ActivationCode) =>
        canManage && row.status === 'unused' ? (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => handleDeleteClick(row.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        ) : null,
    },
  ];

  return (
    <div className="px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Kody aktywacyjne</h1>
          <p className="text-neutral-600">Zarządzanie kodami aktywacyjnymi urządzeń</p>
        </div>
        {canManage && (
          <Button onClick={handleGenerateCode} isLoading={createMutation.isPending}>
            <Plus className="mr-2 h-4 w-4" />
            Wygeneruj kod
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTable
            columns={columns}
            data={codes}
            isLoading={isLoading}
            emptyState={{
              title: 'Brak kodów',
              subtitle: 'Zacznij od wygenerowania pierwszego kodu',
            }}
          />
        </CardContent>
      </Card>

      {/* Dialog pokazujący wygenerowany kod */}
      <Dialog open={showCodeDialog} onOpenChange={handleCloseCodeDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Kod aktywacyjny wygenerowany</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-neutral-600">
              Poniżej znajduje się Twój jednorazowy kod. Skopiuj go i przekaż technikowi.
            </p>
            <div className="rounded-lg bg-neutral-100 p-4">
              <code className="font-mono text-lg font-semibold tracking-wider">
                {generatedCode}
              </code>
            </div>
            <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
              ⚠️ Kod będzie widoczny tylko teraz. Skopiuj go bezpośrednio lub zapisz go bezpiecznie.
            </div>
          </div>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={handleCloseCodeDialog}
            >
              Zamknij
            </Button>
            <Button onClick={handleCopyCode}>
              {copySuccess ? (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Skopiowano
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Kopiuj kod
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog potwierdzenia anulowania */}
      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Anuluj kod"
        description="Ta akcja nie może być cofnięta."
        message="Czy na pewno chcesz anulować ten kod?"
        confirmText="Anuluj"
        cancelText="Nie"
        isDestructive
        isLoading={cancelMutation.isPending}
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
}
