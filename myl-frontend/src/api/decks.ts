import { fetchAPI } from './client';
import type {
  DeckSummary,
  DeckResponse,
  DeckCreateRequest,
  DeckUpdateRequest,
  DeckValidationResult,
} from '../types';

export async function getDecks(): Promise<{ decks: DeckSummary[] }> {
  return fetchAPI<{ decks: DeckSummary[] }>('/mazos');
}

export async function createDeck(deck: DeckCreateRequest): Promise<{ id: number; message: string }> {
  return fetchAPI<{ id: number; message: string }>('/mazos', {
    method: 'POST',
    body: JSON.stringify(deck),
  });
}

export async function getDeck(deckId: number): Promise<DeckResponse> {
  return fetchAPI<DeckResponse>(`/mazos/${deckId}`);
}

export async function updateDeck(deckId: number, deck: DeckUpdateRequest): Promise<{ id: number; message: string }> {
  return fetchAPI<{ id: number; message: string }>(`/mazos/${deckId}`, {
    method: 'PUT',
    body: JSON.stringify(deck),
  });
}

export async function deleteDeck(deckId: number): Promise<void> {
  return fetchAPI<void>(`/mazos/${deckId}`, {
    method: 'DELETE',
  });
}

export async function validateDeck(deckId: number): Promise<DeckValidationResult> {
  return fetchAPI<DeckValidationResult>(`/mazos/${deckId}/validate`);
}
