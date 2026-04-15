import { useEffect, useState } from 'react';
import { useCards } from './hooks/useCards';
import { useAppStore } from './stores/appStore';
import { Layout } from './components/Layout';
import { CardGrid } from './components/Catalog/CardGrid';
import { DeckBuilder } from './components/DeckBuilder/DeckBuilder';
import { Simulator } from './components/Simulator/Simulator';
import { Banlist } from './components/Banlist';
import { Contact } from './components/Contact';

function App() {
  const activeTab = useAppStore((state) => state.activeTab);
  const setActiveTab = useAppStore((state) => state.setActiveTab);
  const catalogFilters = useAppStore((state) => state.catalogFilters);

  const [currentPage, setCurrentPage] = useState(1);

  const { data: cardsData } = useCards({
    ...catalogFilters,
    page: currentPage,
    per_page: 24,
  });

  const cards = cardsData?.cards || [];
  const totalPages = cardsData?.total_pages || 1;

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    // Handle tab switching
    const handleTabClick = (e: Event) => {
      const target = e.currentTarget as HTMLElement;
      const tabElement = target.closest('.nav-tab') as HTMLElement | null;
      const tabName = tabElement?.dataset.tab as string || 'catalog';

      setActiveTab(tabName as any);
    };

    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', handleTabClick);
    });

    return () => {
      document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.removeEventListener('click', handleTabClick);
      });
    };
  }, []);

  return (
    <Layout>
      {activeTab === 'catalog' && (
        <CardGrid
          cards={cards}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      )}
      {activeTab === 'deckbuilder' && <DeckBuilder />}
      {activeTab === 'simulator' && <Simulator />}
      {activeTab === 'banlist' && <Banlist />}
      {activeTab === 'contacto' && <Contact />}
    </Layout>
  );
}

export default App;
