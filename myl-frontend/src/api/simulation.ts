import { fetchAPI } from './client';
import type { SimulationResponse } from '../types';

export async function simulateDraw(deckId: number, drawCount: number = 7): Promise<SimulationResponse> {
  return fetchAPI<SimulationResponse>('/simular', {
    method: 'POST',
    body: JSON.stringify({ deck_id: deckId, draw_count: drawCount }),
  });
}
