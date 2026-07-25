'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { Sparkles } from 'lucide-react'

export default function GenerateCampaignPage() {
  const [objective, setObjective] = useState('awareness')
  const [budget, setBudget] = useState('')
  const [targetAudience, setTargetAudience] = useState('')
  const [productDescription, setProductDescription] = useState('')

  const generateMutation = useMutation({
    mutationFn: () => tauriInvoke<{
      campaign_name?: string;
      strategy_summary?: string;
      platform?: string;
      audience_config?: Record<string, unknown>;
      creatives?: Array<{ copy?: string; headline?: string; variant?: string }>;
    }>('generate_campaign', {
      objective,
      budget: parseFloat(budget) || 100,
      targetAudience: targetAudience || undefined,
      productDescription: productDescription || undefined,
      brandContext: undefined,
    }),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Generar campaña</h1>
        <p className="text-gray-600">La IA diseñará tu campaña publicitaria</p>
      </div>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo</label>
            <select
              className="input"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
            >
              <option value="awareness">Reconocimiento de marca</option>
              <option value="traffic">Tráfico al sitio web</option>
              <option value="conversions">Conversiones / Ventas</option>
              <option value="leads">Generación de leads</option>
              <option value="engagement">Engagement</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Presupuesto ($)</label>
            <input
              type="number"
              className="input"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="500"
              min="1"
            />
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Descripción del producto/servicio
          </label>
          <textarea
            className="input min-h-[80px]"
            value={productDescription}
            onChange={(e) => setProductDescription(e.target.value)}
            placeholder="Describe brevemente lo que ofreces..."
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Público objetivo (opcional)
          </label>
          <input
            className="input"
            value={targetAudience}
            onChange={(e) => setTargetAudience(e.target.value)}
            placeholder="Ej: Mujeres 25-40, interesadas en fitness"
          />
        </div>

        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending || !budget}
          className="btn-primary mt-4 flex items-center gap-2"
        >
          <Sparkles className="h-4 w-4" />
          {generateMutation.isPending ? 'Generando estrategia...' : 'Generar campaña'}
        </button>
      </div>

      {generateMutation.data && (
        <div className="space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-2">
              {(generateMutation.data as any)?.campaign_name}
            </h2>
            <p className="text-gray-600 mb-4">
              {(generateMutation.data as any)?.strategy_summary}
            </p>

            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>Plataforma: <strong className="capitalize">{(generateMutation.data as any)?.platform}</strong></span>
              <span>·</span>
              <span>Presupuesto: <strong>${budget}</strong></span>
            </div>
          </div>

          <h3 className="text-lg font-semibold">Creatividades generadas</h3>
          {(generateMutation.data as any)?.creatives?.map((creative: any, index: number) => (
            <div key={index} className="card">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-brand-100 text-brand-700 text-xs font-medium px-2 py-1 rounded">
                  Variante {creative.variant || String.fromCharCode(65 + index)}
                </span>
              </div>

              {creative.headline && (
                <h4 className="font-semibold text-lg mb-2">{creative.headline}</h4>
              )}
              <p className="text-gray-700 mb-3">{creative.copy}</p>
              {creative.description && (
                <p className="text-sm text-gray-500 mb-3">{creative.description}</p>
              )}
              {creative.cta && (
                <span className="inline-block px-3 py-1 bg-green-100 text-green-700 text-sm rounded font-medium">
                  {creative.cta}
                </span>
              )}
            </div>
          ))}

          <div className="card bg-yellow-50 border border-yellow-200">
            <p className="text-sm text-yellow-800">
              <strong>Nota:</strong> La campaña está en modo borrador. Debes aprobarla antes de que se publique.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
