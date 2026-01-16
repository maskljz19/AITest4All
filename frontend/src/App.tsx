import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Spin } from 'antd'
import ErrorBoundary from './components/ErrorBoundary'
import MainLayout from './components/Layout/MainLayout'
import './App.css'

// Lazy load pages
const Home = lazy(() => import('./pages/Home'))
const Generate = lazy(() => import('./pages/Generate'))
const KnowledgeBase = lazy(() => import('./pages/KnowledgeBase'))
const Scripts = lazy(() => import('./pages/Scripts'))
const Templates = lazy(() => import('./pages/Templates'))
const Settings = lazy(() => import('./pages/Settings'))

// Loading component
const PageLoader = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh' 
  }}>
    <Spin size="large" tip="加载中..." />
  </div>
)

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Home />} />
            <Route path="generate" element={<Generate />} />
            <Route path="knowledge-base" element={<KnowledgeBase />} />
            <Route path="scripts" element={<Scripts />} />
            <Route path="templates" element={<Templates />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}

export default App
