import { useState } from 'react';
import { useCards, useCardSearch } from '../../hooks/useCards';
import { useAppStore } from '../../stores/appStore';
import type { TypeOption } from '../../types';
import { CardImage } from '../CardImage';

export function DeckSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<TypeOption>('');
  const [maxCost, setMaxCost] = useState<number | null>(null);

  const currentDeck = useAppStore((state) => state.currentDeck);
  const setCurrentDeck = useAppStore((state) => state.setCurrentDeck);

  // Use search results when query exists
  const { data: searchData } = useCardSearch(searchTerm, 20, searchTerm.length > 0);
  const { data: filteredData } = useCards({
    search: searchTerm,
    type: typeFilter,
    cost_max: maxCost ?? undefined,
    per_page: 50,
  }, searchTerm.length > 0 || typeFilter !== '' || maxCost !== null);

  const results = searchTerm.length > 0 && searchData?.results ? searchData.results : filteredData?.cards || [];

  const handleAddToDeck = (cardId: number, quantity: number) => {
    if (!currentDeck.id) {
      alert('Crea o selecciona un mazo primero');
      return;
    }

    const existingCard = currentDeck.cards.find((c) => c.card_id === cardId);

    if (existingCard) {
      existingCard.quantity += quantity;
      if (existingCard.quantity > 3) {
        existingCard.quantity = 3;
        alert('Máximo 3 copias por carta');
      }
    } else {
      currentDeck.cards.push({
        card_id: cardId,
        quantity: Math.min(quantity, 3),
      });
    }

    setCurrentDeck({ ...currentDeck });
    alert('Carta agregada al mazo');
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTypeFilter(e.target.value as TypeOption);
  };

  const handleMaxCostChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value ? parseInt(e.target.value) : null;
    setMaxCost(value);
  };

  return (
    <div className="compact-search-panel">
      <input
        type="text"
        className="compact-search-input"
        placeholder="Buscar cartas para agregar..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div style={{ display: 'flex', gap: 'var(--spacing-2)', marginBottom: 'var(--spacing-4)' }}>
        <select
          className="filter-select"
          style={{ flex: 1 }}
          value={typeFilter}
          onChange={handleTypeChange}
        >
          <option value="">Todos los tipos</option>
          <option value="Aliado">Aliado</option>
          <option value="Talismán">Talismán</option>
          <option value="Arma">Arma</option>
          <option value="Tótem">Tótem</option>
          <option value="Oro">Oro</option>
          <option value="Monumento">Monumento</option>
        </select>
        <input
          type="number"
          className="range-input"
          placeholder="Coste máx"
          min="0"
          max="12"
          value={maxCost ?? ''}
          onChange={handleMaxCostChange}
          style={{ width: '100px' }}
        />
      </div>
      <div className="compact-cards-list">
        {results.length === 0 && (
          <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: 'var(--spacing-4)' }}>
            No se encontraron cartas
          </p>
        )}
        {results.map((card) => (
          <div key={card.id} className="compact-card-row">
            <CardImage
              editionId={card.edition_id}
              edid={card.edid}
              alt={card.name}
              className="compact-card-thumb"
            />
            <div className="compact-card-info">
              <div className="compact-card-name">{card.name}</div>
              <div className="compact-card-meta">
                {card.type_name || 'Otro'} · Coste: {card.cost ?? '-'}
              </div>
            </div>
            <div className="compact-card-actions">
              <button
                className="btn btn-primary btn-sm"
                onClick={() => handleAddToDeck(card.id, 1)}
              >
                +1
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => handleAddToDeck(card.id, 3)}
              >
                +3
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
