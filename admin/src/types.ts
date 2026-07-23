export type TipoTrabajo = 'antes_despues' | 'foto';

export interface Catalogo {
  id: number;
  nombre: string;
}

export interface Trabajo {
  id: number;
  categoria_id: number;
  categoria: string;
  titulo: string;
  zona_id: number | null;
  zona: string | null;
  tipo: TipoTrabajo;
  antes_url: string | null;
  despues_url: string | null;
  foto_url: string | null;
  orden: number;
  publicado: boolean;
}

export interface TrabajoInput {
  categoria_id: number;
  titulo: string;
  zona_id: number | null;
  tipo: TipoTrabajo;
  antes_url: string | null;
  despues_url: string | null;
  foto_url: string | null;
  orden: number;
  publicado: boolean;
}
