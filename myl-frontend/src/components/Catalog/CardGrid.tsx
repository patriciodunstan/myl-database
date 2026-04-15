import { useState } from 'react';
import type { Card } from '../../types';
import { CardImage } from '../CardImage';
import { CardModal } from './CardModal';
import { Pagination } from './Pagination';

interface CardGridProps {
  cards: Card[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function CardGrid({ cards, currentPage, totalPages, onPageChange }: CardGridProps) {
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);

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

  const handleCardClick = (card: Card) => {
    setSelectedCard(card);
  };

  const handleCloseModal = () => {
    setSelectedCard(null);
  };

  if (cards.length === 0) {
    return (
      <div className="empty-state">
        <svg className="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
        </svg>
        <h3 className="empty-state-title">No se encontraron cartas</h3>
        <p className="empty-state-message">Intenta ajustar los filtros de búsqueda</p>
      </div>
    );
  }

  return (
    <>
      <div className="cards-grid">
        {cards.map((card) => (
          <div
            key={card.id}
            className="card-item"
            onClick={() => handleCardClick(card)}
          >
            <div className="card-image-container">
              <CardImage
                editionId={card.edition_id}
                edid={card.edid}
                alt={card.name}
                className="card-image"
              />
              {card.printings && card.printings.length > 1 && (
                <span className="editions-badge">{card.printings.length} eds.</span>
              )}
            </div>
            <div className="card-info">
              <div className="card-name">{card.name}</div>
              <div className="card-meta">
                <span className={`card-badge type-${getTypeClass(card.type_name)}`}>
                  {card.type_name}
                </span>
                {card.race_name && (
                  <span className="card-badge">{card.race_name}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
        />
      )}

      {selectedCard && (
        <CardModal
          card={selectedCard}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
}
