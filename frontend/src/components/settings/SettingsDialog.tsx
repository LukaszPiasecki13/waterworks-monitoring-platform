import { useMemo, useState } from 'react'
import { useActivePermissions } from '@/hooks/useActivePermissions'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from '@/components/ui/Dialog'
import { SettingsRail } from './SettingsRail'
import { getPlatformSections, getOrgSections } from './settingsConfig'
import { PlatformUsersPanel } from './panels/PlatformUsersPanel'
import { PlatformGroupsPanel } from './panels/PlatformGroupsPanel'
import { OrgMembersPanel } from './panels/OrgMembersPanel'
import { OrgGroupsPanel } from './panels/OrgGroupsPanel'
import { AccountPanel } from './panels/AccountPanel'

interface SettingsDialogProps {
  scope: 'platform' | 'org'
  open: boolean
  onOpenChange: (open: boolean) => void
}

const panelComponents: Record<string, React.ComponentType> = {
  'platform-users': PlatformUsersPanel,
  'platform-groups': PlatformGroupsPanel,
  'platform-account': AccountPanel,
  'org-members': OrgMembersPanel,
  'org-groups': OrgGroupsPanel,
  'org-account': AccountPanel,
}

export function SettingsDialog({ scope, open, onOpenChange }: SettingsDialogProps) {
  const { permissions } = useActivePermissions()
  const [userSelectedSection, setUserSelectedSection] = useState<string | null>(null)

  const sections = useMemo(() => {
    const baseConfig = scope === 'platform' ? getPlatformSections() : getOrgSections()

    return baseConfig
      .filter((section) => {
        const sectionPerms = Array.isArray(section.permission)
          ? section.permission
          : [section.permission]
        // Empty permission array means everyone has access
        if (sectionPerms.length === 0) return true
        return sectionPerms.some((p) => permissions.includes(p))
      })
      .map((section) => ({
        ...section,
        render: () => {
          const componentKey = scope === 'platform'
            ? `platform-${section.key}`
            : `org-${section.key}`
          const Component = panelComponents[componentKey]
          return Component ? <Component /> : null
        },
      }))
  }, [scope, permissions])

  // Compute active section: reset on open/permission changes, preserve user selection
  const activeSection = useMemo(() => {
    if (!open || sections.length === 0) return null
    if (userSelectedSection && sections.some(s => s.key === userSelectedSection)) {
      return userSelectedSection
    }
    return sections[0].key
  }, [open, sections, userSelectedSection])

  if (sections.length === 0) {
    return null
  }

  const activeTab = sections.find((s) => s.key === activeSection) ?? sections[0]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent size="fullscreen" className="p-0 flex flex-col gap-0">
        <DialogHeader className="border-b border-neutral-200 px-6 py-4 flex-row items-center justify-between">
          <DialogTitle>Ustawienia</DialogTitle>
          <DialogClose />
        </DialogHeader>

        <div className="flex flex-1 min-h-0 overflow-hidden">
          <SettingsRail
            sections={sections}
            activeSection={activeSection || sections[0]?.key || ''}
            onSelectSection={setUserSelectedSection}
          />

          <div className="flex-1 overflow-y-auto bg-white">
            {activeTab.render()}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
