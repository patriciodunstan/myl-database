import { useAppStore } from '../../stores/appStore';

export function DeckList() {
  const currentDeck = useAppStore((state) => state.currentDeck);
  const setCurrentDeck = useAppStore((state) => state.setCurrentDeck);

  const grouped = {
    'Aliado': [],
    'Arma': [],
    'Talismán': [],
    'Tótem': [],
    'Oro': [],
    'Monumento': [],
  } as Record<string, typeof currentDeck.cards>;

  currentDeck.cards.forEach((card) => {
    // Simplified type check - in production we'd fetch full card details
    const type = 'Aliado'; // Default to Aliado for now
    if (!grouped[type]) {
      grouped[type] = [];
    }
    grouped[type].push(card);
  });

  const handleRemoveCard = (cardId: number) => {
    const updatedCards = currentDeck.cards.filter((c) => c.card_id !== cardId);
    setCurrentDeck({
      ...currentDeck,
      cards: updatedCards,
    });
  };

  const handleCardClick = (card: typeof currentDeck.cards[0]) => {
    // Open card detail modal (to be implemented)
    console.log('Card clicked:', card);
  };

  if (currentDeck.cards.length === 0) {
    return (
      <div className="deck-list-container">
        <div className="deck-list-header">
          <span className="deck-list-title">Mazo Actual</span>
          <div className="deck-actions"></div>
        </div>
        <div className="empty-state" style={{ padding: 'var(--spacing-6)' }}>
          <svg className="empty-state-icon" style={{ width: '50px', height: '50px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
          <h4 style={{ color: 'var(--color-text-secondary)', fontFamily: 'var(--font-family-display)' }}>Mazo vacío</h4>
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-small)' }}>Busca cartas para agregarlas</p>
        </div>
      </div>
    );
  }

  return (
    <div className="deck-list-container">
      <div className="deck-list-header">
        <span className="deck-list-title">Mazo Actual</span>
        <div className="deck-actions">
          <button className="btn btn-secondary btn-sm" onClick={() => {
            const exportText = currentDeck.cards
              .map((c) => `${c.quantity}x ${c.card_id}`)
              .join('\n');
            navigator.clipboard.writeText(exportText);
            alert('Mazo copiado al portapapeles');
          }}>
            Exportar
          </button>
        </div>
      </div>

      {Object.entries(grouped).map(([type, cards]) => {
        if (cards.length === 0) return null;

        const typeCount = cards.reduce((sum, card) => sum + card.quantity, 0);

        return (
          <div key={type} className="deck-type-group">
            <div className="deck-type-header">
              <span className="deck-type-name">{type}</span>
              <span className="deck-type-count">{typeCount}</span>
            </div>
            {cards.map((deckCard, index) => (
              <div
                key={`${deckCard.card_id}-${index}`}
                className="deck-card-row"
                onClick={() => handleCardClick(deckCard)}
              >
                <div className="deck-card-info">
                  <span className="deck-card-quantity">{deckCard.quantity}</span>
                  <span className="deck-card-name">{deckCard.card_id}</span>
                </div>
                <div className="deck-card-actions">
                  <button
                    className="quantity-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveCard(deckCard.card_id);
                    }}
                  >
                    -
                  </button>
                </div>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
