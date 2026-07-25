'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { Plus, Check } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function CampaignsPage() {
  const queryClient = useQueryClient()

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: async () => {
      try {
        return await tauriInvoke<any[]>('list_campaigns', { companyId: 'default' })
      } catch {
        return []
      }
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => tauriInvoke('approve_campaign', { campaignId: id }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['campaigns'] }),
  })

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    pending_approval: 'bg-yellow-100 text-yellow-700',
    active: 'bg-green-100 text-green-700',
    paused: 'bg-orange-100 text-orange-700',
    completed: 'bg-blue-100 text-blue-700',
  }

  const statusLabels: Record<string, string> = {
    draft: 'Borrador',
    pending_approval: 'Pendiente aprobación',
    active: 'Activa',
    paused: 'Pausada',
    completed: 'Completada',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campañas publicitarias</h1>
          <p className="text-gray-600">Crea y gestiona campañas con IA</p>
        </div>
        <Link to="/campaigns/generate" className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Generar campaña
        </Link>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto"></div>
          </div>
        ) : campaigns?.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500">No hay campañas todavía</p>
            <Link to="/campaigns/generate" className="btn-primary mt-4 inline-block">
              Crear primera campaña
            </Link>
          </div>
        ) : (
          campaigns?.map((campaign: any) => (
            <div key={campaign.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 bg-brand-50 rounded-lg flex items-center justify-center text-2xl">
                    {campaign.platform === 'instagram' ? '📸' :
                     campaign.platform === 'tiktok' ? '🎵' :
                     campaign.platform === 'twitter' ? '🐦' : '📄'}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{campaign.name}</h3>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span className="capitalize">{campaign.platform}</span>
                      <span>·</span>
                      <span className="capitalize">{campaign.objective}</span>
                      {campaign.budget && (
                        <>
                          <span>·</span>
                          <span>${campaign.budget}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                    statusColors[campaign.status] || 'bg-gray-100 text-gray-700'
                  }`}>
                    {statusLabels[campaign.status] || campaign.status}
                  </span>

                  {!campaign.approved && campaign.status === 'draft' && (
                    <button
                      onClick={() => approveMutation.mutate(campaign.id)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                    >
                      <Check className="h-4 w-4" />
                      Aprobar
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
