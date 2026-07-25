'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { Palette, Globe, Building2, Link2, Unlink } from 'lucide-react'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('brand')

  const tabs = [
    { id: 'brand', label: 'Marca', icon: Palette },
    { id: 'social', label: 'Redes sociales', icon: Globe },
    { id: 'company', label: 'Empresa', icon: Building2 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="text-gray-600">Gestiona tu marca, redes sociales y empresa</p>
      </div>

      <div className="flex gap-6">
        <div className="w-48 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-2 px-4 py-2 text-left rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-brand-50 text-brand-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex-1">
          {activeTab === 'brand' && <BrandSettings />}
          {activeTab === 'social' && <SocialSettings />}
          {activeTab === 'company' && <CompanySettings />}
        </div>
      </div>
    </div>
  )
}

function BrandSettings() {
  const [formData, setFormData] = useState({
    industry: '',
    tone: 'profesional',
    target_audience: '',
    values: '',
    guidelines: '',
  })

  const saveMutation = useMutation({
    mutationFn: () => tauriInvoke('update_brand_profile', {
      companyId: 'default',
      ...formData,
      values: formData.values,
    }),
  })

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Perfil de marca</h2>
      <p className="text-sm text-gray-500 mb-6">
        Configura la identidad de tu marca para que la IA genere contenido coherente
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Industria</label>
          <input
            className="input"
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            placeholder="Ej: Tecnología, Restaurantes, Fitness..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tono de comunicación</label>
          <select
            className="input"
            value={formData.tone}
            onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
          >
            <option value="profesional">Profesional</option>
            <option value="casual">Casual</option>
            <option value="divertido">Divertido</option>
            <option value="serio">Serio</option>
            <option value="inspirador">Inspirador</option>
            <option value="educativo">Educativo</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Público objetivo
          </label>
          <textarea
            className="input min-h-[80px]"
            value={formData.target_audience}
            onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
            placeholder="Describe a tu cliente ideal: edad, intereses, necesidades..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Valores de la marca (separados por coma)
          </label>
          <input
            className="input"
            value={formData.values}
            onChange={(e) => setFormData({ ...formData, values: e.target.value })}
            placeholder="Innovación, Calidad, Confianza..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Guías de estilo
          </label>
          <textarea
            className="input min-h-[80px]"
            value={formData.guidelines}
            onChange={(e) => setFormData({ ...formData, guidelines: e.target.value })}
            placeholder="Instrucciones adicionales para el contenido..."
          />
        </div>

        <button
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending}
          className="btn-primary"
        >
          {saveMutation.isPending ? 'Guardando...' : 'Guardar perfil de marca'}
        </button>
      </div>
    </div>
  )
}

function SocialSettings() {
  const { data: accounts } = useQuery({
    queryKey: ['social-accounts'],
    queryFn: async () => {
      try {
        return await tauriInvoke<any[]>('list_accounts', { companyId: 'default' })
      } catch {
        return []
      }
    },
  })

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Redes sociales conectadas</h2>

      <div className="space-y-3">
        {['instagram', 'tiktok', 'twitter'].map((platform) => {
          const account = accounts?.find((a: any) => a.platform === platform)
          return (
            <div key={platform} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-2xl">
                  {platform === 'instagram' ? '📸' :
                   platform === 'tiktok' ? '🎵' : '🐦'}
                </span>
                <div>
                  <p className="font-medium capitalize">{platform}</p>
                  {account ? (
                    <p className="text-sm text-gray-500">@{account.username}</p>
                  ) : (
                    <p className="text-sm text-gray-400">No conectado</p>
                  )}
                </div>
              </div>

              {account ? (
                <button className="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                  <Unlink className="h-4 w-4" />
                  Desconectar
                </button>
              ) : (
                <button className="flex items-center gap-1 px-3 py-1.5 text-sm text-brand-600 hover:bg-brand-50 rounded-lg">
                  <Link2 className="h-4 w-4" />
                  Conectar
                </button>
              )}
            </div>
          )
        })}
      </div>

      <p className="text-sm text-gray-500 mt-4">
        Conecta tus redes sociales para publicar automáticamente y obtener métricas en tiempo real.
      </p>
    </div>
  )
}

function CompanySettings() {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Información de la empresa</h2>
      <p className="text-sm text-gray-500 mb-6">
        Configura los datos básicos de tu empresa
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de la empresa</label>
          <input className="input" placeholder="Tu empresa" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sitio web</label>
          <input className="input" placeholder="https://tuempresa.com" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
          <textarea className="input min-h-[80px]" placeholder="Describe tu empresa..." />
        </div>

        <button className="btn-primary">Guardar</button>
      </div>
    </div>
  )
}
