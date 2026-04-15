import type { Card, ManaCurveData } from '../../types';

interface ManaCurveProps {
  cards: Card[];
}

export function ManaCurve({ cards }: ManaCurveProps) {
  const calculateManaCurve = (): ManaCurveData => {
    const curve: ManaCurveData = {};

    for (let i = 0; i <= 12; i++) {
      curve[i] = 0;
    }

    cards.forEach((card) => {
      const cost = card.cost ?? 0;
      if (curve[cost] !== undefined) {
        curve[cost] += card.quantity || 0;
      }
    });

    return curve;
  };

  const curve = calculateManaCurve();
  const maxCount = Math.max(...Object.values(curve), 1);

  return (
    <div className="mana-curve">
      <h4 className="mana-curve-title">Curva de Maná</h4>
      <div id="mana-curve-bars" className="mana-curve-bars">
        {Object.entries(curve).map(([cost, count]) => {
          const height = count > 0 ? (count / maxCount) * 100 : 2;
          return (
            <div
              key={cost}
              className="mana-bar"
              style={{ height: `${Math.max(height, 2)}%` }}
              title={`${count} cartas de coste ${cost}`}
            >
              <span className="mana-bar-label">{cost}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
