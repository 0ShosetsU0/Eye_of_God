// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import ProjectDetail from './pages/ProjectDetail'
import DatasetManager from './pages/DatasetManager'
import TrainingPage from './pages/TrainingPage'
import InspectionPage from './pages/InspectionPage'
import Login from './pages/Login'
import Register from './pages/Register'
import Settings from './pages/Settings'
import EditProject from './pages/EditProject'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route path="/" element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="projects/:id" element={<ProjectDetail />} />
          <Route path="projects/:id/dataset" element={<DatasetManager />} />
          <Route path="projects/:id/training" element={<TrainingPage />} />
          <Route path="projects/:id/inspection" element={<InspectionPage />} />
          <Route path="projects/:id/edit" element={<EditProject />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App