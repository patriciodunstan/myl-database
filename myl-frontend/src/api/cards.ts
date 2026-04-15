import { fetchAPI } from './client';
import type {
  Card,
  CardsResponse,
  CardSearchResponse,
} from '../types';

export async function getCards(
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
  } = {}
): Promise<CardsResponse> {
  const queryParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value));
    }
  });

  const queryString = queryParams.toString();
  return fetchAPI<CardsResponse>(`/cartas${queryString ? `?${queryString}` : ''}`);
}

export async function searchCards(query: string, limit: number = 20): Promise<CardSearchResponse> {
  return fetchAPI<CardSearchResponse>(`/cartas/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

export async function getCardDetails(cardId: number): Promise<Card> {
  return fetchAPI<Card>(`/cartas/${cardId}`);
}
