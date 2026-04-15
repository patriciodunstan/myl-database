import { useState } from 'react';
import type { Card } from '../../types';
import { CardImage } from '../CardImage';

interface CardModalProps {
  card: Card;
  onClose: () => void;
}

export function CardModal({ card, onClose }: CardModalProps) {
  const [selectedPrintingId, setSelectedPrintingId] = useState<number>(card.id);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handlePrintingChange = (printing: Card) => {
    setSelectedPrintingId(printing.id);
  };

  const getTypeClass = (typeName: string | null): string => {
    const typeMap: Record<string, string> = {
      'Aliado': 'ally',
      'Arma': 'weapon',
      'Talismán': 'talisman',
      'Tótem': 'totem',
      'Oro': 'gold',
      'Monumento': 'monument',
    };
    return typeMap[typeName || ''] || '';
  };

  const printings = card.printings || [];

  return (
    <div className="modal-backdrop active" onClick={handleBackdropClick}>
      <div className="modal">
        <button className="modal-close" onClick={onClose}>&times;</button>
        <div className="modal-content">
          <div className="card-detail">
            <div className="card-detail-image">
              <CardImage
                editionId={selectedPrintingId === card.id ? card.edition_id : card.edition_id}
                edid={selectedPrintingId === card.id ? card.edid : card.edid}
                alt={card.name}
              />
            </div>
            <div className="card-detail-info">
              <div className="card-detail-header">
                <h2 className="card-detail-name">{card.name}</h2>
                <div className="card-detail-meta">
                  <span className="card-badge">
                    {card.cost !== null ? `Coste: ${card.cost}` : 'Sin coste'}
                  </span>
                  <span className={`card-badge type-${getTypeClass(card.type_name)}`}>
                    {card.type_name}
                  </span>
                  {card.race_name && (
                    <span className="card-badge">{card.race_name}</span>
                  )}
                  {card.rarity_name && (
                    <span className="card-badge">{card.rarity_name}</span>
                  )}
                </div>
              </div>

              {card.ability && (
                <div className="card-detail-section">
                  <h4 className="card-detail-section-title">Habilidad</h4>
                  <p className="card-detail-ability">{card.ability}</p>
                </div>
              )}

              <div className="card-detail-section">
                <h4 className="card-detail-section-title">Estadísticas</h4>
                <div className="card-detail-stats">
                  <div className="stat-row">
                    <span className="stat-row-label">Coste</span>
                    <span className="stat-row-value">{card.cost ?? '-'}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-row-label">Daño</span>
                    <span className="stat-row-value">{card.damage ?? '-'}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-row-label">Fuerza</span>
                    <span className="stat-row-value">-</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-row-label">Resistencia</span>
                    <span className="stat-row-value">-</span>
                  </div>
                </div>
              </div>

              <div className="card-detail-section">
                <h4 className="card-detail-section-title">Información</h4>
                <div className="card-detail-stats">
                  <div className="stat-row">
                    <span className="stat-row-label">Edición</span>
                    <span className="stat-row-value">{card.edition_title}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-row-label">ID Carta</span>
                    <span className="stat-row-value">{card.id}</span>
                  </div>
                </div>
              </div>

              {printings.length > 1 && (
                <div className="card-detail-section">
                  <h4 className="card-detail-section-title">Ediciones disponibles</h4>
                  <div className="modal-printings-list">
                    {printings.map((printing) => (
                      <button
                        key={printing.id}
                        className={`printing-btn ${printing.id === selectedPrintingId ? 'active' : ''}`}
                        onClick={() => handlePrintingChange(printing)}
                      >
                        {printing.edition_title || `Edición ${printing.edition_id}`}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
