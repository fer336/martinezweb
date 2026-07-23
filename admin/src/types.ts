export type Etiqueta = 'antes' | 'despues' | null;

export interface Catalogo {
  id: number;
  nombre: string;
}

export interface TrabajoImagen {
  url: string;
  etiqueta: Etiqueta;
}

export interface Trabajo {
  id: number;
  categoria_id: number;
  categoria: string;
  titulo: string;
  zona_id: number | null;
  zona: string | null;
  orden: number;
  publicado: boolean;
  imagenes: TrabajoImagen[];
}

export interface TrabajoInput {
  categoria_id: number;
  titulo: string;
  zona_id: number | null;
  orden: number;
  publicado: boolean;
  imagenes: TrabajoImagen[];
}
