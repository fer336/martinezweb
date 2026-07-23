import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../api/client';
import AppHeader from '../components/AppHeader';
import ImageTile from '../components/ImageTile';
import { BackIcon } from '../components/Icons';

export default function Portada() {
  const navigate = useNavigate();
  const [heroUrl, setHeroUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getConfig().then((data) => {
      setHeroUrl(data.hero_image_url);
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    if (!heroUrl) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.updateConfig(heroUrl);
      setSaved(true);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <AppHeader
        title="Foto principal"
        left={
          <button className="icon-btn" onClick={() => navigate('/')} aria-label="Volver">
            <BackIcon />
          </button>
        }
      />
      <div className="page">
        {loading ? (
          <p>Cargando…</p>
        ) : (
          <div className="form">
            <p className="preview-label">
              Es la primera foto que ve cualquiera que entre a la web. Se recorta automáticamente al mismo formato
              que tiene ahora, subas la foto que subas.
            </p>
            <ImageTile badge="" url={heroUrl} prefix="hero" onChange={setHeroUrl} />
            {saved && <p className="notice ok">Guardado. Ya se ve en la web.</p>}
          </div>
        )}
      </div>

      {!loading && (
        <div className="bottom-bar">
          <button type="button" className="btn btn-outline" onClick={() => navigate('/')}>
            Volver
          </button>
          <button type="button" className="btn btn-primary" onClick={handleSave} disabled={saving || !heroUrl}>
            {saving ? 'Guardando…' : 'Guardar'}
          </button>
        </div>
      )}
    </>
  );
}
