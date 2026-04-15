import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">Mitos y Leyendas</div>
          <nav className="nav-tabs">
            <button className="nav-tab" data-tab="catalog">Catálogo</button>
            <button className="nav-tab" data-tab="deckbuilder">Constructor</button>
            <button className="nav-tab" data-tab="simulator">Simulador</button>
            <button className="nav-tab" data-tab="banlist">Banlist</button>
            <button className="nav-tab" data-tab="contacto">Contacto</button>
          </nav>
        </div>
      </header>

      <main className="app-main">{children}</main>

      <footer style={{
        textAlign: 'center',
        padding: 'var(--spacing-4)',
        color: 'var(--color-text-muted)',
        fontSize: 'var(--font-size-caption)',
        borderTop: '1px solid var(--color-border)',
        marginTop: 'auto',
      }}>
        Creado por <strong style={{ color: 'var(--color-text-secondary)' }}>patriciods_myl</strong>
      </footer>
    </div>
  );
}
