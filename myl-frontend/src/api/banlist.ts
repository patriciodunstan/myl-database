import { fetchAPI } from './client';
import type { BanlistResponse } from '../types';

export async function getBanlist(format: string = 'racial_edicion'): Promise<BanlistResponse> {
  return fetchAPI<BanlistResponse>(`/banlist?format=${format}`);
}
