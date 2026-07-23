import type { ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import Login from './pages/Login';
import TrabajosList from './pages/TrabajosList';
import TrabajoForm from './pages/TrabajoForm';
import Preview from './pages/Preview';
import Portada from './pages/Portada';

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <TrabajosList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/trabajos/:id"
        element={
          <ProtectedRoute>
            <TrabajoForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/preview"
        element={
          <ProtectedRoute>
            <Preview />
          </ProtectedRoute>
        }
      />
      <Route
        path="/portada"
        element={
          <ProtectedRoute>
            <Portada />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
