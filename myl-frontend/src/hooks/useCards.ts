import { useQuery } from '@tanstack/react-query';
import { getCards, getCardDetails, searchCards } from '../api/cards';

export function useCards(
  params: {
    page?: number;
    per_page?: number;
    search?: string;
    race?: string;
    type?: string;
    edition?: string;
    rarity?: string;
    cost_min?: number | null;
    cost_max?: number | null;
    damage_min?: number | null;
    damage_max?: number | null;
    sort?: string;
  } = {},
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['cards', params],
    queryFn: () => getCards(params),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCardDetails(cardId: number, enabled: boolean = true) {
  return useQuery({
    queryKey: ['card', cardId],
    queryFn: () => getCardDetails(cardId),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useCardSearch(
  query: string,
  limit: number = 20,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['cardSearch', query, limit],
    queryFn: () => searchCards(query, limit),
    enabled: enabled && query.length > 0,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
