import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import * as api from '../api/client';
import type { Trabajo } from '../types';
import { useAuth } from '../auth/AuthContext';
import AppHeader from '../components/AppHeader';
import { LogoutIcon, TrashIcon } from '../components/Icons';

function thumbOf(t: Trabajo): string | null {
  return t.imagenes[0]?.url ?? null;
}

export default function TrabajosList() {
  const [trabajos, setTrabajos] = useState<Trabajo[]>([]);
  const [loading, setLoading] = useState(true);
  const [publishState, setPublishState] = useState<'idle' | 'publishing' | 'ok' | 'error'>('idle');
  const { logout } = useAuth();

  async function reload() {
    setLoading(true);
    const data = await api.listTrabajos();
    setTrabajos(data.sort((a, b) => a.orden - b.orden));
    setLoading(false);
  }

  useEffect(() => {
    reload();
  }, []);

  async function handleDelete(id: number, titulo: string) {
    if (!confirm(`¿Borrar "${titulo}"? No se puede deshacer.`)) return;
    await api.deleteTrabajo(id);
    reload();
  }

  async function handlePublish() {
    setPublishState('publishing');
    try {
      await api.publish();
      setPublishState('ok');
    } catch {
      setPublishState('error');
    }
  }

  return (
    <>
      <AppHeader
        title="Panel de trabajos"
        right={
          <button className="icon-btn" onClick={logout} aria-label="Salir">
            <LogoutIcon />
          </button>
        }
      />
      <div className="page">
        <div className="list-toolbar">
          <div className="list-title">
            <h2>Trabajos</h2>
            {!loading && <span className="count">({trabajos.length})</span>}
          </div>
          <div className="toolbar-row">
            <Link to="/portada" className="btn btn-outline">
              Foto principal
            </Link>
            <Link to="/preview" className="btn btn-outline">
              Vista previa
            </Link>
          </div>
          <button className="btn btn-dark btn-block" onClick={handlePublish} disabled={publishState === 'publishing'}>
            {publishState === 'publishing' ? 'Publicando…' : 'Publicar cambios en la web'}
          </button>
          {publishState === 'ok' && <p className="notice ok">Publicado. La web se actualiza en unos minutos.</p>}
          {publishState === 'error' && <p className="notice error">No se pudo publicar. Revisá la conexión e intentá de nuevo.</p>}
        </div>

        {loading ? (
          <p>Cargando…</p>
        ) : trabajos.length === 0 ? (
          <div className="empty-state">
            <strong>Todavía no cargaste ningún trabajo.</strong>
            <span>Tocá el botón + para subir el primero.</span>
          </div>
        ) : (
          <div className="work-list">
            {trabajos.map((t) => (
              <Link to={`/trabajos/${t.id}`} className="work-row" key={t.id}>
                <div className="work-row-thumb">
                  {thumbOf(t) ? <img src={thumbOf(t)!} alt="" /> : 'Sin foto'}
                </div>
                <div className="work-row-body">
                  <span className="work-row-eyebrow">{t.categoria}</span>
                  <span className="work-row-title">{t.titulo}</span>
                  <span className="work-row-meta">
                    <span className={`status-dot ${t.publicado ? 'publicado' : ''}`} />
                    {t.publicado ? 'Publicado' : 'Borrador'}
                    {t.zona ? ` · ${t.zona}` : ''}
                  </span>
                </div>
                <button
                  className="work-row-delete"
                  aria-label={`Borrar ${t.titulo}`}
                  onClick={(e) => {
                    e.preventDefault();
                    handleDelete(t.id, t.titulo);
                  }}
                >
                  <TrashIcon />
                </button>
              </Link>
            ))}
          </div>
        )}
      </div>

      <Link to="/trabajos/nuevo" className="fab" aria-label="Nuevo trabajo">
        +
      </Link>
    </>
  );
}
