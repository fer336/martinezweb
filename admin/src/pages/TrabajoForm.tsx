import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import * as api from '../api/client';
import type { Catalogo, TipoTrabajo, TrabajoInput } from '../types';
import AppHeader from '../components/AppHeader';
import WorkCard from '../components/WorkCard';
import ImageTile from '../components/ImageTile';
import { BackIcon } from '../components/Icons';

const EMPTY: TrabajoInput = {
  categoria_id: 0,
  titulo: '',
  zona_id: null,
  tipo: 'antes_despues',
  antes_url: null,
  despues_url: null,
  foto_url: null,
  orden: 0,
  publicado: true,
};

function CategoriaField({
  categorias,
  value,
  onChange,
  onCreated,
}: {
  categorias: Catalogo[];
  value: number;
  onChange: (id: number) => void;
  onCreated: (categoria: Catalogo) => void;
}) {
  const [adding, setAdding] = useState(false);
  const [nombre, setNombre] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreate() {
    const value = nombre.trim();
    if (!value) return;
    setCreating(true);
    setError(null);
    try {
      const categoria = await api.createCategoria(value);
      onCreated(categoria);
      setAdding(false);
      setNombre('');
    } catch (err) {
      setError(err instanceof api.ApiError ? err.message : 'No se pudo crear la sección');
    } finally {
      setCreating(false);
    }
  }

  if (adding) {
    return (
      <div className="field">
        Nueva sección
        <div className="inline-add">
          <input
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Ej: Instalaciones eléctricas"
            autoFocus
          />
          <button type="button" className="btn btn-dark" onClick={handleCreate} disabled={creating}>
            {creating ? '…' : 'Agregar'}
          </button>
          <button type="button" className="btn-ghost" onClick={() => setAdding(false)}>
            Cancelar
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>
    );
  }

  return (
    <label className="field">
      Categoría
      <select value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {categorias.map((c) => (
          <option key={c.id} value={c.id}>
            {c.nombre}
          </option>
        ))}
      </select>
      <button type="button" className="link-add" onClick={() => setAdding(true)}>
        + Agregar una sección nueva
      </button>
    </label>
  );
}

export default function TrabajoForm() {
  const { id } = useParams();
  const isNew = !id || id === 'nuevo';
  const navigate = useNavigate();
  const [form, setForm] = useState<TrabajoInput>(EMPTY);
  const [categorias, setCategorias] = useState<Catalogo[]>([]);
  const [zonas, setZonas] = useState<Catalogo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [categoriasList, zonasList] = await Promise.all([api.listCategorias(), api.listZonas()]);
      setCategorias(categoriasList);
      setZonas(zonasList);

      if (!isNew) {
        const items = await api.listTrabajos();
        const found = items.find((t) => t.id === Number(id));
        if (found) {
          setForm({
            categoria_id: found.categoria_id,
            titulo: found.titulo,
            zona_id: found.zona_id,
            tipo: found.tipo,
            antes_url: found.antes_url,
            despues_url: found.despues_url,
            foto_url: found.foto_url,
            orden: found.orden,
            publicado: found.publicado,
          });
        }
      } else if (categoriasList.length > 0) {
        setForm((prev) => ({ ...prev, categoria_id: categoriasList[0].id }));
      }
      setLoading(false);
    }
    load();
  }, [id, isNew]);

  function set<K extends keyof TrabajoInput>(key: K, value: TrabajoInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleTipoChange(tipo: TipoTrabajo) {
    setForm((prev) => ({ ...prev, tipo, antes_url: null, despues_url: null, foto_url: null }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      if (isNew) {
        await api.createTrabajo(form);
      } else {
        await api.updateTrabajo(Number(id), form);
      }
      navigate('/');
    } catch (err) {
      setError(err instanceof api.ApiError ? err.message : 'No se pudo guardar. Revisá la conexión e intentá de nuevo.');
    } finally {
      setSaving(false);
    }
  }

  const categoriaNombre = categorias.find((c) => c.id === form.categoria_id)?.nombre ?? '';

  return (
    <>
      <AppHeader
        title={isNew ? 'Nuevo trabajo' : 'Editar trabajo'}
        left={
          <button className="icon-btn" onClick={() => navigate('/')} aria-label="Volver">
            <BackIcon />
          </button>
        }
      />
      <div className="page form-page">
        {loading ? (
          <p>Cargando…</p>
        ) : (
          <form className="form" id="trabajo-form" onSubmit={handleSubmit}>
            <CategoriaField
              categorias={categorias}
              value={form.categoria_id}
              onChange={(categoria_id) => set('categoria_id', categoria_id)}
              onCreated={(categoria) => {
                setCategorias((prev) => [...prev, categoria].sort((a, b) => a.nombre.localeCompare(b.nombre)));
                set('categoria_id', categoria.id);
              }}
            />

            <label className="field">
              Título
              <input
                value={form.titulo}
                onChange={(e) => set('titulo', e.target.value)}
                placeholder="Ej: Cambio de motor en bomba Rowa"
                required
              />
            </label>

            <label className="field">
              Zona
              <select
                value={form.zona_id ?? ''}
                onChange={(e) => set('zona_id', e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">Sin especificar</option>
                {zonas.map((z) => (
                  <option key={z.id} value={z.id}>
                    {z.nombre}
                  </option>
                ))}
              </select>
            </label>

            <div className="field">
              Tipo de foto
              <div className="segmented">
                <button
                  type="button"
                  className={form.tipo === 'antes_despues' ? 'active' : ''}
                  onClick={() => handleTipoChange('antes_despues')}
                >
                  Antes / después
                </button>
                <button
                  type="button"
                  className={form.tipo === 'foto' ? 'active' : ''}
                  onClick={() => handleTipoChange('foto')}
                >
                  Foto única
                </button>
              </div>
            </div>

            {form.tipo === 'antes_despues' ? (
              <div className="image-fields">
                <ImageTile badge="ANTES" url={form.antes_url} onChange={(url) => set('antes_url', url)} />
                <ImageTile badge="DESPUÉS" url={form.despues_url} onChange={(url) => set('despues_url', url)} />
              </div>
            ) : (
              <div className="image-fields image-fields-single">
                <ImageTile badge="FOTO" url={form.foto_url} onChange={(url) => set('foto_url', url)} />
              </div>
            )}

            <label className="field">
              Orden de aparición
              <input type="number" value={form.orden} onChange={(e) => set('orden', Number(e.target.value))} />
            </label>

            <label className="checkbox-row">
              <input type="checkbox" checked={form.publicado} onChange={(e) => set('publicado', e.target.checked)} />
              Publicado en la web
            </label>

            {error && <p className="error">{error}</p>}

            <div className="preview-block">
              <span className="preview-label">Así se va a ver en la web</span>
              <WorkCard
                categoria={categoriaNombre}
                titulo={form.titulo}
                tipo={form.tipo}
                antesUrl={form.antes_url}
                despuesUrl={form.despues_url}
                fotoUrl={form.foto_url}
              />
            </div>
          </form>
        )}
      </div>

      {!loading && (
        <div className="bottom-bar">
          <button type="button" className="btn btn-outline" onClick={() => navigate('/')}>
            Cancelar
          </button>
          <button type="submit" form="trabajo-form" className="btn btn-primary" disabled={saving}>
            {saving ? 'Guardando…' : 'Guardar'}
          </button>
        </div>
      )}
    </>
  );
}
