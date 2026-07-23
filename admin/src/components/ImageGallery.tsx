import { useState } from 'react';
import * as api from '../api/client';
import type { Etiqueta, TrabajoImagen } from '../types';
import { CameraIcon, ChevronDownIcon, ChevronUpIcon, TrashIcon } from './Icons';

const ETIQUETAS: { value: Etiqueta; label: string }[] = [
  { value: null, label: 'Sin etiqueta' },
  { value: 'antes', label: 'Antes' },
  { value: 'despues', label: 'Después' },
];

export default function ImageGallery({
  imagenes,
  onChange,
}: {
  imagenes: TrabajoImagen[];
  onChange: (imagenes: TrabajoImagen[]) => void;
}) {
  const [uploadingIndex, setUploadingIndex] = useState<number | null>(null);

  async function handlePick(index: number, file: File | undefined) {
    if (!file) return;
    setUploadingIndex(index);
    try {
      const url = await api.uploadImage(file, 'trabajos');
      const next = [...imagenes];
      if (index === imagenes.length) {
        next.push({ url, etiqueta: null });
      } else {
        next[index] = { ...next[index], url };
      }
      onChange(next);
    } finally {
      setUploadingIndex(null);
    }
  }

  function setEtiqueta(index: number, etiqueta: Etiqueta) {
    onChange(imagenes.map((img, i) => (i === index ? { ...img, etiqueta } : img)));
  }

  function remove(index: number) {
    onChange(imagenes.filter((_, i) => i !== index));
  }

  function move(index: number, dir: -1 | 1) {
    const target = index + dir;
    if (target < 0 || target >= imagenes.length) return;
    const next = [...imagenes];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  }

  return (
    <div className="field">
      Fotos del trabajo
      <span className="field-hint">Se van a mostrar rotando en la web, cada 2 segundos.</span>
      <div className="gallery-field">
        {imagenes.map((img, i) => (
          <div className="gallery-item" key={i}>
            <div className="image-tile has-image">
              <img src={img.url} alt="" />
              <label className="picker">
                <span>{uploadingIndex === i ? 'Subiendo…' : 'Cambiar'}</span>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => handlePick(i, e.target.files?.[0])}
                />
              </label>
            </div>
            <div className="gallery-item-controls">
              <select value={img.etiqueta ?? ''} onChange={(e) => setEtiqueta(i, (e.target.value || null) as Etiqueta)}>
                {ETIQUETAS.map((op) => (
                  <option key={op.label} value={op.value ?? ''}>
                    {op.label}
                  </option>
                ))}
              </select>
              <div className="gallery-item-actions">
                <button type="button" onClick={() => move(i, -1)} disabled={i === 0} aria-label="Mover antes">
                  <ChevronUpIcon size={16} />
                </button>
                <button
                  type="button"
                  onClick={() => move(i, 1)}
                  disabled={i === imagenes.length - 1}
                  aria-label="Mover después"
                >
                  <ChevronDownIcon size={16} />
                </button>
                <button type="button" onClick={() => remove(i)} aria-label="Quitar foto" className="danger">
                  <TrashIcon size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}

        <div className="image-tile gallery-add">
          <label className="picker">
            {uploadingIndex === imagenes.length ? (
              <span>Subiendo…</span>
            ) : (
              <>
                <CameraIcon />
                <span>Agregar foto</span>
              </>
            )}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => handlePick(imagenes.length, e.target.files?.[0])}
            />
          </label>
        </div>
      </div>
    </div>
  );
}
