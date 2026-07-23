import { useEffect, useState } from 'react';
import type { TrabajoImagen } from '../types';

interface WorkCardProps {
  categoria: string;
  titulo: string;
  imagenes: TrabajoImagen[];
}

export default function WorkCard({ categoria, titulo, imagenes }: WorkCardProps) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    setActive(0);
    if (imagenes.length < 2) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const id = setInterval(() => setActive((i) => (i + 1) % imagenes.length), 2000);
    return () => clearInterval(id);
  }, [imagenes]);

  return (
    <div className="work-card">
      <div className="work-gallery">
        {imagenes.length === 0 ? (
          <div className="work-slide is-active" />
        ) : (
          imagenes.map((img, i) => (
            <div className={`work-slide${i === active ? ' is-active' : ''}`} key={img.url + i}>
              <img
                src={img.url}
                alt={img.etiqueta === 'antes' ? `Antes: ${titulo}` : img.etiqueta === 'despues' ? `Después: ${titulo}` : titulo}
              />
              {img.etiqueta && <span className="badge">{img.etiqueta === 'antes' ? 'ANTES' : 'DESPUÉS'}</span>}
            </div>
          ))
        )}
      </div>
      <div className="work-info">
        <span className="eyebrow">{categoria.toUpperCase()}</span>
        <strong>{titulo || 'Título del trabajo'}</strong>
      </div>
    </div>
  );
}
