import { useEffect, useMemo, useState } from 'react'
import { cn } from '@/lib/cn'
import { Switch } from '@/components/ui/Switch'
import { Button } from '@/components/ui/Button'
import { toast } from '@/components/ui/Toast'
import type { SecurityGroupSummary, SecurityPermission } from '@/types/coreData'

interface GroupPermissionsTabProps {
  group: SecurityGroupSummary
  availablePermissions: SecurityPermission[]
  onSave: (permissionCodes: string[]) => Promise<void>
}

export function GroupPermissionsTab({
  group,
  availablePermissions,
  onSave,
}: GroupPermissionsTabProps) {
  const [selectedCodes, setSelectedCodes] = useState<string[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const permissionsByCategory = useMemo(() => {
    const groups = new Map<string, SecurityPermission[]>()
    for (const permission of availablePermissions) {
      const list = groups.get(permission.category) ?? []
      list.push(permission)
      groups.set(permission.category, list)
    }
    return Array.from(groups.entries()).sort((a, b) => a[0].localeCompare(b[0]))
  }, [availablePermissions])

  useEffect(() => {
    setSelectedCodes(group.permissions.map((p) => p.code))
    setSaveError(null)
  }, [group.id, group.permissions])

  const hasChanges = useMemo(() => {
    const currentCodes = new Set(group.permissions.map((p) => p.code))
    const selectedSet = new Set(selectedCodes)
    if (currentCodes.size !== selectedSet.size) return true
    for (const code of currentCodes) {
      if (!selectedSet.has(code)) return true
    }
    return false
  }, [group.permissions, selectedCodes])

  const togglePermission = (code: string) => {
    setSelectedCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    )
  }

  const handleSave = async () => {
    try {
      setIsSaving(true)
      setSaveError(null)
      await onSave(selectedCodes)
      toast.success('Uprawnienia zaktualizowane')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Nie udało się zapisać uprawnień'
      setSaveError(message)
      toast.error(message)
      setSelectedCodes(group.permissions.map((p) => p.code))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="flex flex-col flex-1 min-h-0 gap-4 px-6 py-4">
      <div className="flex-1 flex flex-col overflow-hidden">
        {permissionsByCategory.length === 0 ? (
          <div className="p-8 text-center text-sm text-neutral-500 flex-1 flex items-center justify-center">
            Brak dostępnych uprawnień
          </div>
        ) : (
          <div className="divide-y divide-neutral-200 overflow-y-auto scrollbar-hide flex-1">
            {permissionsByCategory.map(([category, permissions]) => {
              const checkedCount = permissions.filter((p) =>
                selectedCodes.includes(p.code)
              ).length

              return (
                <div key={category} className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold text-neutral-900">
                      {category}
                    </h4>
                    <span className="text-xs font-mono text-neutral-500 bg-neutral-100 px-2 py-1 rounded">
                      {checkedCount}/{permissions.length}
                    </span>
                  </div>
                  <div className="space-y-3">
                    {permissions.map((permission) => {
                      const isChecked = selectedCodes.includes(permission.code)
                      return (
                        <div
                          key={permission.code}
                          className="flex items-center justify-between py-2"
                        >
                          <label className="text-sm text-neutral-900 cursor-pointer flex-1">
                            {permission.name}
                          </label>
                          <Switch
                            checked={isChecked}
                            onCheckedChange={() => togglePermission(permission.code)}
                            disabled={group.is_system}
                          />
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {group.is_system && (
        <div className="text-xs text-neutral-500 p-3 bg-neutral-50 rounded-md border border-neutral-200">
          🔒 Uprawnienia grupy systemowej są ustalone i tylko do odglądu — przełączniki aktywują
          się dopiero dla grup własnych.
        </div>
      )}

      {hasChanges && !group.is_system && (
        <div className={cn(
          'p-3 rounded-md border flex items-center justify-between',
          saveError
            ? 'bg-red-50 border-red-200 text-red-900'
            : 'bg-yellow-50 border-yellow-200 text-yellow-900'
        )}>
          <span className="text-sm font-medium">
            {saveError
              ? `Błąd: ${saveError}`
              : 'Niezapisane zmiany'}
          </span>
          <Button
            size="sm"
            onClick={handleSave}
            isLoading={isSaving}
            disabled={isSaving}
            variant={saveError ? 'destructive' : 'primary'}
          >
            {saveError ? 'Spróbuj ponownie' : 'Zapisz'}
          </Button>
        </div>
      )}
    </div>
  )
}
