'use client'

import { useQuery } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { Users, Eye, Heart, TrendingUp, AlertTriangle } from 'lucide-react'

export default function AnalyticsPage() {
  const { data: overview } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: async () => {
      try {
        return await tauriInvoke<any>('get_overview', { companyId: 'default', days: 30 })
      } catch {
        return { total_followers: 0, total_reach: 0, total_engagement: 0, engagement_rate: 0, platforms: [] }
      }
    },
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      try {
        return await tauriInvoke<any[]>('get_alerts', { companyId: 'default' })
      } catch {
        return []
      }
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Métricas y rendimiento de tus redes sociales</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total seguidores</p>
              <p className="text-2xl font-bold">{overview?.total_followers || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-50 rounded-lg">
              <Eye className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Alcance total</p>
              <p className="text-2xl font-bold">{(overview?.total_reach || 0).toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-pink-50 rounded-lg">
              <Heart className="h-6 w-6 text-pink-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Engagement</p>
              <p className="text-2xl font-bold">{(overview?.total_engagement || 0).toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Tasa engagement</p>
              <p className="text-2xl font-bold">{overview?.engagement_rate || 0}%</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Rendimiento por plataforma</h2>
        <div className="space-y-4">
          {overview?.platforms?.map((platform: any) => (
            <div key={platform.platform} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-2xl">
                  {platform.platform === 'instagram' ? '📸' :
                   platform.platform === 'tiktok' ? '🎵' :
                   platform.platform === 'twitter' ? '🐦' : '📄'}
                </span>
                <div>
                  <p className="font-medium capitalize">{platform.platform}</p>
                  <p className="text-sm text-gray-500">@{platform.username || 'No conectado'}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold">{platform.followers?.toLocaleString()} seguidores</p>
                <p className="text-sm text-gray-500">
                  {platform.reach?.toLocaleString() || 0} alcance
                </p>
              </div>
            </div>
          ))}
          {(!overview?.platforms || overview.platforms.length === 0) && (
            <p className="text-center text-gray-500 py-8">
              Conecta tus redes sociales para ver métricas
            </p>
          )}
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Alertas recientes</h2>
          <span className="flex items-center gap-1 text-sm text-gray-500">
            <AlertTriangle className="h-4 w-4" />
            {alerts?.filter((a: any) => !a.acknowledged).length || 0} pendientes
          </span>
        </div>
        <div className="space-y-3">
          {alerts?.slice(0, 5).map((alert: any) => (
            <div key={alert.id} className={`p-4 rounded-lg ${
              alert.severity === 'critical' ? 'bg-red-50 border border-red-200' :
              alert.severity === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
              'bg-blue-50 border border-blue-200'
            }`}>
              <p className="font-medium">{alert.title}</p>
              <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
              {alert.explanation && (
                <p className="text-sm text-gray-500 mt-2 italic">{alert.explanation}</p>
              )}
            </div>
          ))}
          {(!alerts || alerts.length === 0) && (
            <p className="text-center text-gray-500 py-8">No hay alertas</p>
          )}
        </div>
      </div>
    </div>
  )
}
