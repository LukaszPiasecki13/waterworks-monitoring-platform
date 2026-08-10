import { useNavigate } from 'react-router-dom'
import { ObjectsStatusTable } from '@/components/dashboard/ObjectsStatusTable'

export function DashboardPage() {
  const navigate = useNavigate()

  const handleSelectObject = (objectId: string) => {
    navigate(`/objects/${objectId}`)
  }

  return (
    <div className="px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitorowanie sieci wodociągów w czasie rzeczywistym</p>
      </div>

      <div className="grid gap-6">
        <ObjectsStatusTable onSelectObject={handleSelectObject} />
      </div>
    </div>
  )
}
