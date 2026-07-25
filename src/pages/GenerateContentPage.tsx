'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { Sparkles, Copy, Check } from 'lucide-react'

export default function GenerateContentPage() {
  const [platform, setPlatform] = useState('instagram')
  const [contentType, setContentType] = useState('post')
  const [topic, setTopic] = useState('')
  const [includeImage, setIncludeImage] = useState(false)
  const [copied, setCopied] = useState<number | null>(null)

  const generateMutation = useMutation({
    mutationFn: () => tauriInvoke<{
      variations?: Array<{
        title?: string;
        body?: string;
        hashtags?: string[];
        cta?: string;
        best_time?: string;
      }>;
    }>('generate_content', {
      platform,
      contentType,
      topic: topic || undefined,
      numVariations: 3,
      brandContext: undefined,
    }),
  })

  const handleGenerate = () => {
    generateMutation.mutate()
  }

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopied(index)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Generar contenido</h1>
        <p className="text-gray-600">Usa IA para crear contenido personalizado</p>
      </div>

      {/* Generator form */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plataforma</label>
            <select
              className="input"
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
            >
              <option value="instagram">Instagram</option>
              <option value="tiktok">TikTok</option>
              <option value="twitter">Twitter / X</option>
              <option value="facebook">Facebook</option>
              <option value="linkedin">LinkedIn</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de contenido</label>
            <select
              className="input"
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
            >
              <option value="post">Post</option>
              <option value="reel">Reel / Video</option>
              <option value="story">Story</option>
              <option value="carousel">Carrusel</option>
              <option value="tweet">Tweet</option>
              <option value="blog">Blog</option>
              <option value="newsletter">Newsletter</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tema o idea (opcional)
          </label>
          <input
            className="input"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Ej: Tips de productividad para emprendedores"
          />
        </div>

        <div className="mt-4 flex items-center gap-2">
          <input
            type="checkbox"
            id="includeImage"
            checked={includeImage}
            onChange={(e) => setIncludeImage(e.target.checked)}
            className="rounded border-gray-300 text-brand-600"
          />
          <label htmlFor="includeImage" className="text-sm text-gray-700">
            Generar imagen con DALL-E
          </label>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending}
          className="btn-primary mt-4 flex items-center gap-2"
        >
          <Sparkles className="h-4 w-4" />
          {generateMutation.isPending ? 'Generando...' : 'Generar contenido'}
        </button>
      </div>

      {/* Results */}
      {generateMutation.data && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Variaciones generadas</h2>

          {(generateMutation.data as any)?.variations?.map((variation: any, index: number) => (
            <div key={index} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-brand-100 text-brand-700 text-xs font-medium px-2 py-1 rounded">
                      Variación {index + 1}
                    </span>
                    {variation.best_time && (
                      <span className="text-xs text-gray-500">
                        Mejor hora: {variation.best_time}
                      </span>
                    )}
                  </div>

                  <h3 className="font-semibold text-lg mb-2">{variation.title}</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{variation.body}</p>

                  {variation.hashtags?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {variation.hashtags.map((tag: string) => (
                        <span key={tag} className="text-sm text-brand-600">#{tag}</span>
                      ))}
                    </div>
                  )}

                  {variation.cta && (
                    <p className="mt-3 text-sm font-medium text-green-700">
                      CTA: {variation.cta}
                    </p>
                  )}
                </div>

                <button
                  onClick={() => copyToClipboard(
                    `${variation.title}\n\n${variation.body}\n\n${variation.hashtags?.map((t: string) => `#${t}`).join(' ')}`,
                    index
                  )}
                  className="p-2 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg"
                >
                  {copied === index ? (
                    <Check className="h-5 w-5 text-green-500" />
                  ) : (
                    <Copy className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
