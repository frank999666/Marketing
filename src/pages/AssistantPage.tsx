'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { tauriInvoke } from '../lib/tauri'
import { Send, Bot, User } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  suggestions?: string[]
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hola! Soy tu asistente de marketing digital. Puedo ayudarte a analizar tus métricas, sugerir contenido, optimizar campañas y responder preguntas sobre tu estrategia. ¿En qué puedo ayudarte?',
      suggestions: [
        '¿Qué debería publicar esta semana?',
        '¿Qué red social está funcionando mejor?',
        '¿Dónde conviene invertir mi presupuesto?',
      ],
    },
  ])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const chatMutation = useMutation({
    mutationFn: (message: string) => tauriInvoke<{ answer: string; suggestions: string[] }>('chat', {
      companyId: 'default',
      message,
    }),
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.answer,
        suggestions: data.suggestions,
      }])
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = (message?: string) => {
    const text = message || input
    if (!text.trim()) return

    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    }])
    setInput('')
    chatMutation.mutate(text)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Asistente IA</h1>
        <p className="text-gray-600">Tu director de marketing digital personal</p>
      </div>

      <div className="flex-1 card flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}
            >
              {message.role === 'assistant' && (
                <div className="h-8 w-8 bg-brand-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-brand-600" />
                </div>
              )}

              <div className={`max-w-[70%] ${
                message.role === 'user'
                  ? 'bg-brand-600 text-white rounded-2xl rounded-br-sm'
                  : 'bg-gray-100 text-gray-900 rounded-2xl rounded-bl-sm'
              } px-4 py-3`}>
                <p className="whitespace-pre-wrap">{message.content}</p>

                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(suggestion)}
                        className="text-sm bg-white text-brand-600 px-3 py-1.5 rounded-full hover:bg-brand-50 border border-brand-200"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
              )}
            </div>
          ))}

          {chatMutation.isPending && (
            <div className="flex gap-3">
              <div className="h-8 w-8 bg-brand-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-brand-600" />
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1">
                  <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t p-4">
          <div className="flex gap-2">
            <input
              className="input flex-1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Escribe tu pregunta..."
              disabled={chatMutation.isPending}
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || chatMutation.isPending}
              className="btn-primary px-4"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            El asistente usa los datos reales de tu empresa para responder
          </p>
        </div>
      </div>
    </div>
  )
}
