import { invoke } from '@tauri-apps/api/core'

// Tauri IPC adapter - transparent layer for API calls
export const tauriInvoke = async <T>(command: string, args?: Record<string, unknown>): Promise<T> => {
  return invoke<T>(command, args)
}

// API adapter that works with Tauri IPC
export const api = {
  post: async (path: string, data?: any) => {
    const command = pathToCommand(path)
    const result = await tauriInvoke(command, data || {})
    return { data: result }
  },

  get: async (path: string, params?: any) => {
    const command = pathToCommand(path)
    const result = await tauriInvoke(command, params || {})
    return { data: result }
  },

  put: async (path: string, data?: any) => {
    const command = pathToCommand(path)
    const result = await tauriInvoke(command, data || {})
    return { data: result }
  },

  delete: async (path: string) => {
    const command = pathToCommand(path)
    const result = await tauriInvoke(command)
    return { data: result }
  },
}

// Convert API path to Tauri command name
function pathToCommand(path: string): string {
  // Remove leading slash and convert to snake_case
  const cleaned = path.replace(/^\/+/, '').replace(/-/g, '_')

  // Map API paths to Tauri commands
  const commandMap: Record<string, string> = {
    'auth/login': 'login',
    'auth/register': 'register',
    'auth/me': 'get_me',
    'content': 'list_posts',
    'content/generate': 'generate_content',
    'content/generate_image': 'generate_image',
    'social/accounts': 'list_accounts',
    'social/connect': 'connect_account',
    'social/publish': 'publish_post',
    'social/analytics/overview': 'get_analytics_overview',
    'analytics/overview': 'get_overview',
    'analytics/trends': 'get_trends',
    'analytics/alerts': 'get_alerts',
    'campaigns': 'list_campaigns',
    'campaigns/generate': 'generate_campaign',
    'assistant/chat': 'chat',
    'reports': 'list_reports',
    'reports/generate': 'generate_report',
    'brand-profile': 'get_brand_profile',
    'settings/company': 'get_company',
  }

  return commandMap[cleaned] || cleaned
}

// Content API
export const contentApi = {
  list: (params?: { platform?: string; status?: string }) =>
    api.get('/content', params),
  get: (id: string) => api.get(`/content/${id}`),
  create: (data: any) => api.post('/content', data),
  update: (id: string, data: any) => api.put(`/content/${id}`, data),
  delete: (id: string) => api.delete(`/content/${id}`),
  generate: (data: any) => api.post('/content/generate', data),
  generateImage: (data: any) => api.post('/content/generate_image', data),
}

// Social API
export const socialApi = {
  accounts: () => api.get('/social/accounts'),
  connect: (data: any) => api.post('/social/connect', data),
  disconnect: (id: string) => api.delete(`/social/accounts/${id}`),
  publish: (data: any) => api.post('/social/publish', data),
  analytics: () => api.get('/social/analytics/overview'),
}

// Analytics API
export const analyticsApi = {
  overview: (days?: number) => api.get('/analytics/overview', { days }),
  trends: (metric: string, days?: number) =>
    api.get('/analytics/trends', { metric, days }),
  alerts: (acknowledged?: boolean) =>
    api.get('/analytics/alerts', { acknowledged }),
  acknowledgeAlert: (id: string) => api.put(`/analytics/alerts/${id}/acknowledge`),
}

// Campaigns API
export const campaignsApi = {
  list: () => api.get('/campaigns'),
  get: (id: string) => api.get(`/campaigns/${id}`),
  create: (data: any) => api.post('/campaigns', data),
  update: (id: string, data: any) => api.put(`/campaigns/${id}`, data),
  approve: (id: string) => api.post(`/campaigns/${id}/approve`),
  generate: (data: any) => api.post('/campaigns/generate', data),
}

// Assistant API
export const assistantApi = {
  chat: (message: string, context?: any) =>
    api.post('/assistant/chat', { message, context }),
}

// Reports API
export const reportsApi = {
  list: () => api.get('/reports'),
  get: (id: string) => api.get(`/reports/${id}`),
  generate: (data: any) => api.post('/reports/generate', data),
}

// Settings API
export const settingsApi = {
  getBrandProfile: () => api.get('/brand-profile'),
  updateBrandProfile: (data: any) => api.put('/brand-profile', data),
  getCompany: () => api.get('/settings/company'),
  updateCompany: (data: any) => api.put('/settings/company', data),
}
