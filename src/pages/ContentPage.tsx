'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Plus, Trash2, Link } from 'lucide-react'
import { tauriInvoke } from '../lib/tauri'

export default function ContentPage() {
  const queryClient = useQueryClient()
  const [platformFilter, setPlatformFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: posts, isLoading } = useQuery({
    queryKey: ['posts', platformFilter, statusFilter],
    queryFn: async () => {
      try {
        return await tauriInvoke<any[]>('list_posts', {
          companyId: 'default',
          platform: platformFilter || undefined,
          status: statusFilter || undefined,
        })
      } catch {
        return []
      }
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => tauriInvoke('delete_post', { postId: id }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['posts'] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contenido</h1>
          <p className="text-gray-600">Gestiona todo tu contenido de marketing</p>
        </div>
        <Link to="/content/generate" className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Generar contenido
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          className="input max-w-xs"
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value)}
        >
          <option value="">Todas las plataformas</option>
          <option value="instagram">Instagram</option>
          <option value="tiktok">TikTok</option>
          <option value="twitter">Twitter</option>
          <option value="facebook">Facebook</option>
          <option value="linkedin">LinkedIn</option>
        </select>

        <select
          className="input max-w-xs"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">Todos los estados</option>
          <option value="draft">Borradores</option>
          <option value="scheduled">Programados</option>
          <option value="published">Publicados</option>
        </select>
      </div>

      {/* Content list */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600 mx-auto"></div>
          </div>
        ) : posts?.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500">No hay contenido todavía</p>
            <Link to="/content/generate" className="btn-primary mt-4 inline-block">
              Generar primer contenido
            </Link>
          </div>
        ) : (
          posts?.map((post: any) => (
            <div key={post.id} className="card flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                  {post.platform === 'instagram' ? '📸' :
                   post.platform === 'tiktok' ? '🎵' :
                   post.platform === 'twitter' ? '🐦' : '📄'}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{post.title || 'Sin título'}</h3>
                  <p className="text-sm text-gray-500 line-clamp-1">{post.body?.substring(0, 100)}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{post.platform}</span>
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{post.content_type}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                  post.status === 'published' ? 'bg-green-100 text-green-700' :
                  post.status === 'scheduled' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {post.status}
                </span>
                <button
                  onClick={() => deleteMutation.mutate(post.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
