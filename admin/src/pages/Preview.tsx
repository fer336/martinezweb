import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../api/client';
import type { Trabajo } from '../types';
import AppHeader from '../components/AppHeader';
import WorkCard from '../components/WorkCard';
import { BackIcon } from '../components/Icons';

export default function Preview() {
  const [trabajos, setTrabajos] = useState<Trabajo[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.listTrabajos().then((data) => {
      setTrabajos(data.filter((t) => t.publicado).sort((a, b) => a.orden - b.orden));
      setLoading(false);
    });
  }, []);

  return (
    <>
      <AppHeader
        title="Vista previa"
        left={
          <button className="icon-btn" onClick={() => navigate('/')} aria-label="Volver">
            <BackIcon />
          </button>
        }
      />
      <div className="page">
        <p className="preview-label" style={{ marginBottom: 16 }}>
          Así se ve la sección "Trabajos realizados" con lo publicado ahora mismo
        </p>
        {loading ? (
          <p>Cargando…</p>
        ) : trabajos.length === 0 ? (
          <div className="empty-state">
            <strong>Todavía no hay nada publicado.</strong>
            <span>Marcá "Publicado en la web" en algún trabajo para verlo acá.</span>
          </div>
        ) : (
          <div className="preview-grid">
            {trabajos.map((t) => (
              <WorkCard
                key={t.id}
                categoria={t.categoria}
                titulo={t.titulo}
                tipo={t.tipo}
                antesUrl={t.antes_url}
                despuesUrl={t.despues_url}
                fotoUrl={t.foto_url}
              />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
