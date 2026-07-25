'use client'

import { useQuery } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import {
  Users,
  Eye,
  Heart,
  TrendingUp,
  Calendar,
  PenTool,
  Megaphone,
} from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { data: overview } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: async () => {
      try {
        const result = await tauriInvoke<any>('get_overview', { companyId: 'default', days: 30 })
        return result
      } catch {
        return { total_followers: 0, total_reach: 0, total_engagement: 0, engagement_rate: 0, platforms: [] }
      }
    },
  })

  const { data: posts } = useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      try {
        const result = await tauriInvoke<any[]>('list_posts', { companyId: 'default', status: 'published' })
        return result
      } catch {
        return []
      }
    },
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      try {
        const result = await tauriInvoke<any[]>('get_alerts', { companyId: 'default', acknowledged: false })
        return result
      } catch {
        return []
      }
    },
  })

  const stats = [
    {
      name: 'Seguidores',
      value: overview?.total_followers || 0,
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      name: 'Alcance',
      value: (overview?.total_reach || 0).toLocaleString(),
      icon: Eye,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
    {
      name: 'Engagement',
      value: (overview?.total_engagement || 0).toLocaleString(),
      icon: Heart,
      color: 'text-pink-600',
      bg: 'bg-pink-50',
    },
    {
      name: 'Tasa de Engagement',
      value: `${overview?.engagement_rate || 0}%`,
      icon: TrendingUp,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Resumen de tu marketing digital</p>
        </div>
        <Link to="/content/generate" className="btn-primary">
          Generar contenido
        </Link>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent posts */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Publicaciones recientes</h2>
            <Link to="/content" className="text-brand-600 text-sm hover:underline">
              Ver todo
            </Link>
          </div>
          <div className="space-y-3">
            {posts?.slice(0, 5).map((post: any) => (
              <div key={post.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 bg-brand-100 rounded-lg flex items-center justify-center">
                    <PenTool className="h-5 w-5 text-brand-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{post.title || 'Sin título'}</p>
                    <p className="text-sm text-gray-500">{post.platform} · {post.content_type}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  post.status === 'published' ? 'bg-green-100 text-green-700' :
                  post.status === 'scheduled' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {post.status}
                </span>
              </div>
            ))}
            {(!posts || posts.length === 0) && (
              <p className="text-center text-gray-500 py-8">
                No hay publicaciones aún. ¡Genera tu primer contenido!
              </p>
            )}
          </div>
        </div>

        {/* Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Alertas</h2>
            <Link to="/analytics" className="text-brand-600 text-sm hover:underline">
              Ver todas
            </Link>
          </div>
          <div className="space-y-3">
            {alerts?.slice(0, 5).map((alert: any) => (
              <div key={alert.id} className={`p-3 rounded-lg ${
                alert.severity === 'critical' ? 'bg-red-50 border border-red-200' :
                alert.severity === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                'bg-blue-50 border border-blue-200'
              }`}>
                <p className="font-medium text-sm">{alert.title}</p>
                <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
              </div>
            ))}
            {(!alerts || alerts.length === 0) && (
              <p className="text-center text-gray-500 py-8">
                No hay alertas pendientes
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/content/generate" className="card hover:shadow-md transition-shadow cursor-pointer group">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-brand-50 rounded-lg group-hover:bg-brand-100 transition-colors">
              <PenTool className="h-6 w-6 text-brand-600" />
            </div>
            <div>
              <h3 className="font-semibold">Generar contenido</h3>
              <p className="text-sm text-gray-500">Crea posts con IA para cualquier red</p>
            </div>
          </div>
        </Link>

        <Link to="/calendar" className="card hover:shadow-md transition-shadow cursor-pointer group">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-lg group-hover:bg-purple-100 transition-colors">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold">Calendario</h3>
              <p className="text-sm text-gray-500">Programa tus publicaciones</p>
            </div>
          </div>
        </Link>

        <Link to="/campaigns/generate" className="card hover:shadow-md transition-shadow cursor-pointer group">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-50 rounded-lg group-hover:bg-green-100 transition-colors">
              <Megaphone className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold">Crear campaña</h3>
              <p className="text-sm text-gray-500">Diseña campañas publicitarias con IA</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}
