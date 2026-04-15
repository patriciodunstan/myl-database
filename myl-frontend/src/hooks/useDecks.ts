import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDecks, createDeck, getDeck, updateDeck, deleteDeck, validateDeck } from '../api/decks';
import type { DeckCreateRequest, DeckUpdateRequest } from '../types';

export function useDecks(enabled: boolean = true) {
  return useQuery({
    queryKey: ['decks'],
    queryFn: getDecks,
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDeck(deckId: number | null, enabled: boolean = true) {
  return useQuery({
    queryKey: ['deck', deckId],
    queryFn: () => (deckId ? getDeck(deckId) : Promise.reject('No deck ID')),
    enabled: enabled && deckId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateDeck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deck: DeckCreateRequest) => createDeck(deck),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
    },
  });
}

export function useUpdateDeck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ deckId, deck }: { deckId: number; deck: DeckUpdateRequest }) =>
      updateDeck(deckId, deck),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
      queryClient.invalidateQueries({ queryKey: ['deck'] });
    },
  });
}

export function useDeleteDeck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deckId: number) => deleteDeck(deckId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decks'] });
    },
  });
}

export function useValidateDeck() {
  return useMutation({
    mutationFn: (deckId: number) => validateDeck(deckId),
  });
}
