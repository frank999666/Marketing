'use client'

import { useState } from 'react'
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react'

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date())

  const daysInMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth() + 1,
    0
  ).getDate()

  const firstDayOfMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth(),
    1
  ).getDay()

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]

  const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))
  }

  const events: { [key: number]: { title: string; platform: string; color: string }[] } = {
    5: [{ title: 'Post motivacional', platform: 'Instagram', color: 'bg-pink-100 text-pink-700' }],
    12: [
      { title: 'Tutorial video', platform: 'TikTok', color: 'bg-gray-100 text-gray-700' },
      { title: 'Hilo tips', platform: 'Twitter', color: 'bg-blue-100 text-blue-700' },
    ],
    18: [{ title: 'Carrusel educativo', platform: 'Instagram', color: 'bg-pink-100 text-pink-700' }],
    25: [{ title: 'Newsletter semanal', platform: 'Email', color: 'bg-green-100 text-green-700' }],
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Calendario editorial</h1>
          <p className="text-gray-600">Planifica y programa tu contenido</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Nuevo post
        </button>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-lg">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <h2 className="text-xl font-semibold">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h2>
          <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-lg">
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {dayNames.map((day) => (
            <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: firstDayOfMonth }).map((_, i) => (
            <div key={`empty-${i}`} className="h-24 bg-gray-50 rounded-lg" />
          ))}

          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1
            const isToday =
              day === new Date().getDate() &&
              currentDate.getMonth() === new Date().getMonth() &&
              currentDate.getFullYear() === new Date().getFullYear()
            const dayEvents = events[day] || []

            return (
              <div
                key={day}
                className={`h-24 border rounded-lg p-2 cursor-pointer hover:bg-gray-50 transition-colors ${
                  isToday ? 'border-brand-500 bg-brand-50' : 'border-gray-200'
                }`}
              >
                <span className={`text-sm font-medium ${
                  isToday ? 'text-brand-600' : 'text-gray-700'
                }`}>
                  {day}
                </span>
                <div className="mt-1 space-y-1">
                  {dayEvents.map((event, idx) => (
                    <div
                      key={idx}
                      className={`text-xs px-1.5 py-0.5 rounded truncate ${event.color}`}
                    >
                      {event.title}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
