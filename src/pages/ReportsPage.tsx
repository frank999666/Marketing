'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { useState } from 'react'
import { FileText, Calendar } from 'lucide-react'

export default function ReportsPage() {
  const queryClient = useQueryClient()
  const [reportType, setReportType] = useState('weekly')

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      try {
        return await tauriInvoke<any[]>('list_reports', { companyId: 'default' })
      } catch {
        return []
      }
    },
  })

  const generateMutation = useMutation({
    mutationFn: () => tauriInvoke('generate_report', { companyId: 'default', reportType }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reports'] }),
  })

  const typeLabels: Record<string, string> = {
    daily: 'Diario',
    weekly: 'Semanal',
    monthly: 'Mensual',
    executive: 'Ejecutivo',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reportes</h1>
          <p className="text-gray-600">Reportes automáticos de tu rendimiento</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="input max-w-xs"
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
          >
            <option value="daily">Diario</option>
            <option value="weekly">Semanal</option>
            <option value="monthly">Mensual</option>
            <option value="executive">Ejecutivo</option>
          </select>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="btn-primary"
          >
            {generateMutation.isPending ? 'Generando...' : 'Generar reporte'}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto"></div>
          </div>
        ) : reports?.length === 0 ? (
          <div className="card text-center py-12">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No hay reportes todavía</p>
            <p className="text-sm text-gray-400 mt-1">Genera tu primer reporte para ver el análisis</p>
          </div>
        ) : (
          reports?.map((report: any) => (
            <div key={report.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 bg-brand-50 rounded-lg flex items-center justify-center">
                    <FileText className="h-6 w-6 text-brand-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">
                      Reporte {typeLabels[report.report_type] || report.report_type}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar className="h-4 w-4" />
                      <span>{report.period_start} - {report.period_end}</span>
                    </div>
                  </div>
                </div>

                <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                  report.status === 'generated' ? 'bg-green-100 text-green-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {report.status === 'generated' ? 'Generado' : report.status}
                </span>
              </div>

              {report.content && (
                <div className="mt-4 pt-4 border-t grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Posts totales</p>
                    <p className="text-lg font-semibold">{report.content.summary?.total_posts || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Alcance total</p>
                    <p className="text-lg font-semibold">
                      {(report.content.metrics?.total_reach || 0).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Engagement</p>
                    <p className="text-lg font-semibold">
                      {(report.content.metrics?.total_engagement || 0).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Tasa engagement</p>
                    <p className="text-lg font-semibold">
                      {report.content.metrics?.engagement_rate || 0}%
                    </p>
                  </div>
                </div>
              )}

              {report.content?.recommendations?.length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-medium text-gray-700 mb-2">Recomendaciones:</p>
                  <ul className="space-y-1">
                    {report.content.recommendations.map((rec: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-brand-500 mt-0.5">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
