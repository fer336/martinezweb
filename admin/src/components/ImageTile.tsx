import { useState } from 'react';
import * as api from '../api/client';
import { CameraIcon } from './Icons';

export default function ImageTile({
  badge,
  url,
  prefix = 'trabajos',
  onChange,
}: {
  badge: string;
  url: string | null;
  prefix?: 'trabajos' | 'hero';
  onChange: (url: string) => void;
}) {
  const [uploading, setUploading] = useState(false);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setUploading(true);
    try {
      const uploadedUrl = await api.uploadImage(file, prefix);
      onChange(uploadedUrl);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className={`image-tile ${url ? 'has-image' : ''}`}>
      {badge && <span className="badge">{badge}</span>}
      {url && <img src={url} alt={badge || 'Foto'} />}
      <label className="picker">
        {!url && <CameraIcon />}
        <span>{uploading ? 'Subiendo…' : url ? 'Cambiar foto' : 'Sacar / elegir foto'}</span>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </label>
    </div>
  );
}
