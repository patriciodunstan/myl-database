import { create } from 'zustand';
import type {
  Tab,
  CurrentDeck,
  CatalogFilters,
  SimulatorState,
  Card,
} from '../types';

interface AppStore {
  // Catalog state
  activeTab: Tab;
  catalogFilters: CatalogFilters;

  // Deck builder state
  currentDeck: CurrentDeck;

  // Simulator state
  simulator: SimulatorState;

  // Actions
  setActiveTab: (tab: Tab) => void;
  setCatalogFilters: (filters: Partial<CatalogFilters>) => void;
  resetCatalogFilters: () => void;
  setCurrentDeck: (deck: CurrentDeck) => void;
  resetCurrentDeck: () => void;
  setSimulatorDeck: (deck: Card[] | null) => void;
  setSimulatorHand: (hand: Card[], remaining: number) => void;
  resetSimulator: () => void;
}

const initialCatalogFilters: CatalogFilters = {
  search: '',
  race: '',
  type: '',
  edition: '',
  rarity: '',
  costMin: null,
  costMax: null,
  powerMin: null,
  powerMax: null,
  sort: 'name',
};

const initialCurrentDeck: CurrentDeck = {
  id: null,
  name: '',
  race: '',
  format: 'racial_edicion',
  cards: [],
};

const initialSimulatorState: SimulatorState = {
  deck: null,
  hand: [],
  deckRemaining: 0,
};

export const useAppStore = create<AppStore>((set) => ({
  // Initial state
  activeTab: 'catalog',
  catalogFilters: { ...initialCatalogFilters },
  currentDeck: { ...initialCurrentDeck },
  simulator: { ...initialSimulatorState },

  // Catalog actions
  setActiveTab: (tab) => set({ activeTab: tab }),
  setCatalogFilters: (filters) => set((state) => ({
    catalogFilters: { ...state.catalogFilters, ...filters },
  })),
  resetCatalogFilters: () => set({ catalogFilters: { ...initialCatalogFilters } }),

  // Deck builder actions
  setCurrentDeck: (deck) => set({ currentDeck: deck }),
  resetCurrentDeck: () => set({ currentDeck: { ...initialCurrentDeck } }),

  // Simulator actions
  setSimulatorDeck: (deckCards) => set((state) => ({
    simulator: {
      ...state.simulator,
      deck: deckCards
        ? {
            id: 0,
            name: 'Simulator Deck',
            race: '',
            format: '',
            created_at: '',
            updated_at: '',
            cards_count: deckCards.length,
            ally_count: deckCards.filter((c) => c.type_name === 'Aliado').length,
          }
        : null,
      deckRemaining: deckCards ? deckCards.reduce((sum, c) => sum + (c.quantity || 0), 0) : 0,
    },
  })),
  setSimulatorHand: (hand, remaining) => set((state) => ({
    simulator: {
      ...state.simulator,
      hand,
      deckRemaining: remaining,
    },
  })),
  resetSimulator: () => set((state) => ({
    simulator: {
      ...state.simulator,
      hand: [],
      deckRemaining: state.simulator.deck
        ? state.simulator.deck.cards_count || 0
        : 0,
    },
  })),
}));
