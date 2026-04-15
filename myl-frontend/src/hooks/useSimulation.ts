import { useMutation } from '@tanstack/react-query';
import { simulateDraw } from '../api/simulation';
import type { SimulationResponse, SimulationRequest } from '../types';

export function useSimulation() {
  return useMutation<SimulationResponse, Error, SimulationRequest>({
    mutationFn: (request: SimulationRequest) => simulateDraw(request.deck_id, request.draw_count),
  });
}
