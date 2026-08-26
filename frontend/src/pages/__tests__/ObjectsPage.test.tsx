import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import type { UseQueryResult } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'
import { ObjectsPage } from '../ObjectsPage'
import * as useTelemetryApiModule from '@/hooks/useTelemetryApi'
import * as useWaterObjectsModule from '@/hooks/useWaterObjects'
import * as useActivePermissionsModule from '@/hooks/useActivePermissions'
import * as useOrgIdModule from '@/hooks/useOrgId'
import type { WaterObject } from '@/types/coreData'
import type { PaginatedResponse, ObjectSummary } from '@/types/telemetry'
import type { PermissionCode } from '@/types/permissions'

const mockTelemetryData = {
  items: [
    {
      org_id: 'org-1',
      org_name: 'Test Org',
      object_id: 'obj-1',
      name: 'Test Object',
      device_id: 'dev-1',
      device_name: 'Device 1',
      status: 'ok' as const,
      last_contact_at: new Date().toISOString(),
      last_measurement_at: new Date().toISOString(),
      points: [],
    },
  ],
}

const mockWaterObjects = {
  data: [
    {
      id: 'obj-1',
      organization_id: 'org-1',
      name: 'Test Object',
      object_type: 'pump',
      location_description: 'Test Location',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
}

const mockPermissions = ['CAN_VIEW_ASSETS']

function renderWithProviders(component: React.ReactNode) {
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    </BrowserRouter>
  )
}

describe('ObjectsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(useTelemetryApiModule, 'useTelemetryObjects').mockReturnValue({
      data: mockTelemetryData,
      isPending: false,
      isLoading: false,
      isError: false,
      error: null,
      status: 'success' as const,
    } as unknown as UseQueryResult<PaginatedResponse<ObjectSummary>, Error>)

    vi.spyOn(useWaterObjectsModule, 'useWaterObjects').mockReturnValue({
      data: mockWaterObjects.data,
      isPending: false,
      isLoading: false,
      isError: false,
      error: null,
      status: 'success' as const,
    } as unknown as UseQueryResult<WaterObject[], Error>)

    vi.spyOn(useActivePermissionsModule, 'useActivePermissions').mockReturnValue({
      permissions: mockPermissions as PermissionCode[],
      hasPermission: (permission: PermissionCode) => mockPermissions.includes(permission),
      hasAnyPermission: (permissions: PermissionCode[]) =>
        permissions.some((p) => mockPermissions.includes(p)),
    })

    vi.spyOn(useOrgIdModule, 'useOrgId').mockReturnValue('org-1')
  })

  it('renders toggle buttons for grid and list mode', () => {
    renderWithProviders(<ObjectsPage />)
    expect(screen.getByRole('button', { name: /siatka/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /lista/i })).toBeInTheDocument()
  })

  it('toggle grid/list mode changes view', async () => {
    const user = userEvent.setup()
    renderWithProviders(<ObjectsPage />)

    const listButton = screen.getByRole('button', { name: /lista/i })
    await user.click(listButton)

    const gridButton = screen.getByRole('button', { name: /siatka/i })
    await user.click(gridButton)
    // After clicking grid button, it should have primary styling
    expect(gridButton).toHaveClass('bg-brand-500')
  })

  it('calls useTelemetryObjects and useWaterObjects hooks', () => {
    renderWithProviders(<ObjectsPage />)
    expect(useTelemetryApiModule.useTelemetryObjects).toHaveBeenCalled()
    expect(useWaterObjectsModule.useWaterObjects).toHaveBeenCalled()
  })

  it('renders without crashing when in grid mode', () => {
    renderWithProviders(<ObjectsPage />)
    // Grid mode should render with grid button styled as primary
    expect(screen.getByRole('button', { name: /siatka/i })).toHaveClass('bg-brand-500')
  })

  it('renders without crashing when in list mode', async () => {
    const user = userEvent.setup()
    renderWithProviders(<ObjectsPage />)
    await user.click(screen.getByRole('button', { name: /lista/i }))
    // After switching to list mode, list button should have primary styling
    expect(screen.getByRole('button', { name: /lista/i })).toHaveClass('bg-brand-500')
  })
})
