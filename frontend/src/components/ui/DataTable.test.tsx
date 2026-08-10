import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { DataTable } from './DataTable'

describe('DataTable', () => {
  const mockData = [
    { id: '1', name: 'Row 1', value: 100 },
    { id: '2', name: 'Row 2', value: 200 },
  ]

  const mockColumns = [
    { key: 'name', label: 'Name', render: (row: any) => row.name },
    { key: 'value', label: 'Value', render: (row: any) => row.value },
  ]

  it('renders table headers', () => {
    render(<DataTable columns={mockColumns} data={mockData} />)
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Value')).toBeInTheDocument()
  })

  it('renders table rows', () => {
    render(<DataTable columns={mockColumns} data={mockData} />)
    expect(screen.getByText('Row 1')).toBeInTheDocument()
    expect(screen.getByText('Row 2')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('200')).toBeInTheDocument()
  })

  it('handles empty data', () => {
    render(<DataTable columns={mockColumns} data={[]} />)
    expect(screen.getByText(/Brak danych|No data/i)).toBeInTheDocument()
  })

  it('shows loading state', () => {
    const { container } = render(<DataTable columns={mockColumns} data={mockData} isLoading={true} />)
    expect(container.querySelector('[class*="animate"]')).toBeInTheDocument()
  })

  it('triggers onRowClick callback', () => {
    const handleRowClick = vi.fn()
    render(
      <DataTable
        columns={mockColumns}
        data={mockData}
        onRowClick={handleRowClick}
      />
    )
    const firstRow = screen.getByText('Row 1').closest('tr')
    if (firstRow) {
      firstRow.click()
      expect(handleRowClick).toHaveBeenCalled()
    }
  })
})
