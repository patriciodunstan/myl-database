// ========================================
// DOMAIN TYPES
// ========================================

export interface Card {
  id: number;
  edid: string;
  slug: string;
  name: string;
  edition_id: number;
  race_id: number | null;
  type_id: number | null;
  rarity_id: number | null;
  cost: number | null;
  damage: number | null;
  ability: string | null;
  flavour: string | null;
  keywords: string | null;
  image_path: string | null;
  edition_title: string;
  edition_slug: string;
  race_name: string | null;
  race_slug: string | null;
  type_name: string | null;
  type_slug: string | null;
  rarity_name: string | null;
  rarity_slug: string | null;
  printings?: Card[];
  quantity?: number; // For deck card counts
}

export interface CardsResponse {
  cards: Card[];
  total: number;
  page: number;
  total_pages: number;
}

export interface CardSearchResponse {
  results: Card[];
}

export interface Edition {
  id: number;
  title: string;
  slug: string;
}

export interface EditionsResponse {
  editions: Edition[];
}

export interface DeckSummary {
  id: number;
  name: string;
  race: string | null;
  format: string;
  created_at: string;
  updated_at: string;
  cards_count?: number;
  ally_count?: number;
  cards?: Card[];
}

export interface DeckCardsRequest {
  card_id: number;
  quantity: number;
}

export interface DeckCreateRequest {
  name: string;
  race: string;
  format: string;
  cards: DeckCardsRequest[];
}

export interface DeckUpdateRequest {
  name: string;
  race: string;
  format: string;
  cards: DeckCardsRequest[];
}

export interface DeckCard extends Card {
  id: number;
  deck_id: number;
  card_id: number;
  quantity: number;
}

export interface DeckResponse {
  id: number;
  name: string;
  race: string | null;
  format: string;
  created_at: string;
  updated_at: string;
  cards: DeckCard[];
}

export interface DecksResponse {
  decks: DeckSummary[];
}

export interface DeckValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  card_count: number;
  ally_count: number;
}

export interface BanlistEntry {
  card_name: string;
  edition: string | null;
  restriction: 'prohibida' | 'limitada_1' | 'limitada_2' | 'sin_restriccion';
  limit?: number;
}

export interface BanlistResponse {
  banlist: BanlistEntry[];
}

export interface ContactForm {
  nombre: string;
  email: string;
  tipo: string;
  mensaje: string;
}

export interface ContactResponse {
  message: string;
}

export interface SimulationRequest {
  deck_id: number;
  draw_count: number;
}

export interface SimulationResponse {
  hand: Card[];
  remaining: number;
  deck_size: number;
}

export interface StatsResponse {
  total_cards: number;
  total_editions: number;
}

// ========================================
// STATE & FILTER TYPES
// ========================================

export type Tab = 'catalog' | 'deckbuilder' | 'simulator' | 'banlist' | 'contacto';

export type RaceOption =
  | ''
  | 'Sin Raza'
  | 'Caballero'
  | 'Bestia'
  | 'Eterno'
  | 'Guerrero'
  | 'Bárbaro'
  | 'Faerie'
  | 'Sombra'
  | 'Dragón'
  | 'Héroe'
  | 'Olímpico'
  | 'Titán'
  | 'Faraón'
  | 'Sacerdote'
  | 'Defensor'
  | 'Desafiante'
  | 'Anciano'
  | 'Profano';

export type TypeOption = '' | 'Aliado' | 'Talismán' | 'Arma' | 'Tótem' | 'Oro' | 'Monumento';

export type RarityOption = '' | 'Común' | 'Infrecuente' | 'Rara' | 'Mítica' | 'Legendaria' | 'Promo';

export type SortOption = 'name' | 'cost' | 'damage' | 'edition';

export type FormatOption = 'racial_edicion' | 'racial_libre' | 'formato_libre';

export type ContactTypeOption = 'Sugerencia' | 'Consulta' | 'Reporte de error' | 'Otro';

export interface CatalogFilters {
  search: string;
  race: RaceOption;
  type: TypeOption;
  edition: string;
  rarity: RarityOption;
  costMin: number | null;
  costMax: number | null;
  powerMin: number | null;
  powerMax: number | null;
  sort: SortOption;
}

export interface CurrentDeck {
  id: number | null;
  name: string;
  race: RaceOption;
  format: FormatOption;
  cards: DeckCardsRequest[];
}

export interface SimulatorState {
  deck: DeckSummary | null;
  hand: Card[];
  deckRemaining: number;
}

// ========================================
// UI COMPONENT PROPS
// ========================================

export interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  onClose?: () => void;
}

export interface CardImageProps {
  editionId: number;
  edid: string;
  alt: string;
  className?: string;
  loading?: 'lazy' | 'eager';
}

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export interface ManaCurveData {
  [cost: number]: number;
}
