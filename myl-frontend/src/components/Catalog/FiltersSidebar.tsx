import type { CatalogFilters, RaceOption, TypeOption, RarityOption, SortOption } from '../../types';

interface FiltersSidebarProps {
  filters: CatalogFilters;
  onFiltersChange: (filters: Partial<CatalogFilters>) => void;
  onReset: () => void;
  isCollapsed?: boolean;
}

const RACE_OPTIONS: RaceOption[] = [
  '',
  'Sin Raza',
  'Caballero',
  'Bestia',
  'Eterno',
  'Guerrero',
  'Bárbaro',
  'Faerie',
  'Sombra',
  'Dragón',
  'Héroe',
  'Olímpico',
  'Titán',
  'Faraón',
  'Sacerdote',
];

const TYPE_OPTIONS: TypeOption[] = [
  '',
  'Aliado',
  'Talismán',
  'Arma',
  'Tótem',
  'Oro',
  'Monumento',
];

const RARITY_OPTIONS: RarityOption[] = [
  '',
  'Común',
  'Infrecuente',
  'Rara',
  'Mítica',
  'Legendaria',
  'Promo',
];

const SORT_OPTIONS: SortOption[] = ['name', 'cost', 'damage', 'edition'];

export function FiltersSidebar({ filters, onFiltersChange, onReset, isCollapsed = false }: FiltersSidebarProps) {
  const handleFilterChange = (key: keyof CatalogFilters, value: string | number | null) => {
    onFiltersChange({ [key]: value });
  };

  const handleRangeChange = (key: 'costMin' | 'costMax' | 'powerMin' | 'powerMax', value: string) => {
    const numValue = value === '' ? null : parseInt(value, 10);
    onFiltersChange({ [key]: numValue });
  };

  return (
    <aside className={`filters-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="filters-header">
        <span className="filters-title">Filtros</span>
        <button className="filters-toggle">▼</button>
      </div>
      <div className="filters-content">
        <div className="filter-group">
          <label className="filter-label">Raza</label>
          <select
            className="filter-select"
            value={filters.race}
            onChange={(e) => handleFilterChange('race', e.target.value)}
          >
            {RACE_OPTIONS.map((race) => (
              <option key={race} value={race}>
                {race || 'Todas'}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Tipo</label>
          <select
            className="filter-select"
            value={filters.type}
            onChange={(e) => handleFilterChange('type', e.target.value)}
          >
            {TYPE_OPTIONS.map((type) => (
              <option key={type} value={type}>
                {type || 'Todos'}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Rareza</label>
          <select
            className="filter-select"
            value={filters.rarity}
            onChange={(e) => handleFilterChange('rarity', e.target.value)}
          >
            {RARITY_OPTIONS.map((rarity) => (
              <option key={rarity} value={rarity}>
                {rarity || 'Todas'}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Coste</label>
          <div className="range-filter">
            <input
              type="number"
              className="range-input"
              placeholder="0"
              min="0"
              max="12"
              value={filters.costMin ?? ''}
              onChange={(e) => handleRangeChange('costMin', e.target.value)}
            />
            <span>-</span>
            <input
              type="number"
              className="range-input"
              placeholder="12"
              min="0"
              max="12"
              value={filters.costMax ?? ''}
              onChange={(e) => handleRangeChange('costMax', e.target.value)}
            />
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Ordenar por</label>
          <select
            className="filter-select"
            value={filters.sort}
            onChange={(e) => handleFilterChange('sort', e.target.value)}
          >
            {SORT_OPTIONS.map((sort) => (
              <option key={sort} value={sort}>
                {sort === 'name' && 'Nombre'}
                {sort === 'cost' && 'Coste'}
                {sort === 'damage' && 'Daño'}
                {sort === 'edition' && 'Edición'}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-actions">
          <button className="btn btn-primary btn-sm">Aplicar</button>
          <button className="btn btn-secondary btn-sm" onClick={onReset}>
            Limpiar
          </button>
        </div>
      </div>
    </aside>
  );
}
