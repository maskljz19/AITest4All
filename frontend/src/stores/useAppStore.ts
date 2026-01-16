/**
 * Global Application State Store
 */
import { create } from 'zustand'

interface AppState {
  // User info (if needed in future)
  user: any | null
  setUser: (user: any) => void

  // Global loading
  globalLoading: boolean
  setGlobalLoading: (loading: boolean) => void

  // Sidebar collapsed state
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),

  globalLoading: false,
  setGlobalLoading: (loading) => set({ globalLoading: loading }),

  sidebarCollapsed: false,
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
}))

export default useAppStore
