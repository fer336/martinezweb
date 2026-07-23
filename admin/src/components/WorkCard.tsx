interface WorkCardProps {
  categoria: string;
  titulo: string;
  tipo: 'antes_despues' | 'foto';
  antesUrl?: string | null;
  despuesUrl?: string | null;
  fotoUrl?: string | null;
}

export default function WorkCard({ categoria, titulo, tipo, antesUrl, despuesUrl, fotoUrl }: WorkCardProps) {
  return (
    <div className="work-card">
      {tipo === 'antes_despues' ? (
        <div className="work-photos">
          <figure className="work-photo">
            {antesUrl && <img src={antesUrl} alt={`Antes: ${titulo}`} />}
            <figcaption>ANTES</figcaption>
          </figure>
          <figure className="work-photo">
            {despuesUrl && <img src={despuesUrl} alt={`Después: ${titulo}`} />}
            <figcaption>DESPUÉS</figcaption>
          </figure>
        </div>
      ) : (
        <div className="work-photos work-photos-single">
          <figure className="work-photo">{fotoUrl && <img src={fotoUrl} alt={titulo} />}</figure>
        </div>
      )}
      <div className="work-info">
        <span className="eyebrow">{categoria.toUpperCase()}</span>
        <strong>{titulo || 'Título del trabajo'}</strong>
      </div>
    </div>
  );
}
