import { useQuery } from '@tanstack/react-query';
import { getBanlist } from '../api/banlist';

export function useBanlist(format: string = 'racial_edicion', enabled: boolean = true) {
  return useQuery({
    queryKey: ['banlist', format],
    queryFn: () => getBanlist(format),
    enabled,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}
