import { useEffect } from 'react';
import { useDecks, useCreateDeck, useUpdateDeck, useValidateDeck } from '../../hooks/useDecks';
import { useAppStore } from '../../stores/appStore';
import { DeckList } from './DeckList';
import { DeckSearch } from './DeckSearch';

export function DeckBuilder() {
  const { data: decksData } = useDecks();
  const createDeckMutation = useCreateDeck();
  const updateDeckMutation = useUpdateDeck();
  const validateDeckMutation = useValidateDeck();
  
  const currentDeck = useAppStore((state) => state.currentDeck);
  const setCurrentDeck = useAppStore((state) => state.setCurrentDeck);
  const resetCurrentDeck = useAppStore((state) => state.resetCurrentDeck);

  const decks = decksData?.decks || [];

  useEffect(() => {
    if (currentDeck.id && decks.length > 0) {
      const deck = decks.find((d) => d.id === currentDeck.id);
      if (deck) {
        setCurrentDeck({
          ...currentDeck,
          name: deck.name,
          race: deck.race as any || '',
          format: deck.format as any || 'racial_edicion',
        });
      }
    }
  }, [currentDeck.id, decks, setCurrentDeck]);

  const handleNewDeck = () => {
    resetCurrentDeck();
  };

  const handleDeckSelect = (deckId: string) => {
    if (!deckId) {
      resetCurrentDeck();
      return;
    }

    const deck = decks.find((d) => d.id === parseInt(deckId));
    if (deck) {
      setCurrentDeck({
        id: deck.id,
        name: deck.name,
        race: deck.race as any || '',
        format: deck.format as any || 'racial_edicion',
        cards: [],
      });
    }
  };

  const handleSaveDeck = async () => {
    if (!currentDeck.name) {
      alert('El mazo necesita un nombre');
      return;
    }

    try {
      if (currentDeck.id) {
        await updateDeckMutation.mutateAsync({
          deckId: currentDeck.id,
          deck: {
            name: currentDeck.name,
            race: currentDeck.race,
            format: currentDeck.format,
            cards: currentDeck.cards,
          },
        });
      } else {
        const result = await createDeckMutation.mutateAsync({
          name: currentDeck.name,
          race: currentDeck.race,
          format: currentDeck.format,
          cards: currentDeck.cards,
        });
        setCurrentDeck({
          ...currentDeck,
          id: result.id,
        });
      }
      alert('Mazo guardado correctamente');
    } catch (error) {
      alert('Error al guardar el mazo');
    }
  };

  const handleValidateDeck = async () => {
    if (!currentDeck.id) {
      alert('Guarda el mazo primero');
      return;
    }

    try {
      const result = await validateDeckMutation.mutateAsync(currentDeck.id);
      if (result.valid) {
        alert('¡El mazo es válido!');
      } else {
        alert(`Errores:\n${result.errors.join('\n')}\n\nAdvertencias:\n${result.warnings.join('\n')}`);
      }
    } catch (error) {
      alert('Error al validar el mazo');
    }
  };

  const handleDeckInfoChange = (field: 'name' | 'race' | 'format', value: string) => {
    setCurrentDeck({
      ...currentDeck,
      [field]: value,
    });
  };

  const totalCards = currentDeck.cards.reduce((sum, card) => sum + card.quantity, 0);
  const allyCards = currentDeck.cards.reduce((sum, card) => sum + card.quantity, 0);

  return (
    <div className="deck-builder-container">
      <div className="deck-sidebar">
        <div className="deck-selector">
          <div className="deck-selector-header">
            <span className="deck-selector-title">Mazos</span>
            <button className="btn btn-primary btn-sm" onClick={handleNewDeck}>
              + Nuevo
            </button>
          </div>
          <select
            className="filter-select"
            value={currentDeck.id ?? ''}
            onChange={(e) => handleDeckSelect(e.target.value)}
          >
            <option value="">Seleccionar mazo...</option>
            {decks.map((deck) => (
              <option key={deck.id} value={deck.id}>{deck.name}</option>
            ))}
          </select>
        </div>

        <div className="deck-info-panel">
          <div className="deck-input-group">
            <label>Nombre del Mazo</label>
            <input
              type="text"
              className="deck-name-input"
              value={currentDeck.name}
              placeholder="Ej: Caballeros Agresivos"
              onChange={(e) => handleDeckInfoChange('name', e.target.value)}
            />
          </div>

          <div className="deck-input-group">
            <label>Raza</label>
            <select
              className="filter-select"
              value={currentDeck.race}
              onChange={(e) => handleDeckInfoChange('race', e.target.value)}
            >
              <option value="">Sin Raza</option>
              <option value="Caballero">Caballero</option>
              <option value="Bestia">Bestia</option>
              <option value="Eterno">Eterno</option>
              <option value="Guerrero">Guerrero</option>
              <option value="Bárbaro">Bárbaro</option>
              <option value="Faerie">Faerie</option>
              <option value="Sombra">Sombra</option>
              <option value="Dragón">Dragón</option>
              <option value="Héroe">Héroe</option>
              <option value="Olímpico">Olímpico</option>
              <option value="Titán">Titán</option>
              <option value="Faraón">Faraón</option>
              <option value="Sacerdote">Sacerdote</option>
            </select>
          </div>

          <div className="deck-input-group">
            <label>Formato</label>
            <select
              className="filter-select"
              value={currentDeck.format}
              onChange={(e) => handleDeckInfoChange('format', e.target.value)}
            >
              <option value="racial_edicion">Racial Edición</option>
              <option value="racial_libre">Racial Libre</option>
              <option value="formato_libre">Formato Libre</option>
            </select>
          </div>

          <div className="deck-stats-grid">
            <div className="deck-stat" id="total-cards-stat">
              <div className="deck-stat-value">{totalCards}</div>
              <div className="deck-stat-label">Cartas</div>
            </div>
            <div className="deck-stat" id="ally-count-stat">
              <div className="deck-stat-value">{allyCards}</div>
              <div className="deck-stat-label">Aliados</div>
            </div>
            <div className="deck-stat">
              <div className="deck-stat-value">60</div>
              <div className="deck-stat-label">Mínimo</div>
            </div>
            <div className="deck-stat">
              <div className="deck-stat-value">16</div>
              <div className="deck-stat-label">Aliados Mín</div>
            </div>
          </div>

          <div className="filter-actions" style={{ marginTop: 'var(--spacing-4)' }}>
            <button className="btn btn-secondary btn-sm" onClick={handleValidateDeck}>
              Validar
            </button>
            <button className="btn btn-primary btn-sm" onClick={handleSaveDeck}>
              Guardar
            </button>
          </div>
        </div>

        <DeckList />
      </div>

      <DeckSearch />
    </div>
  );
}
