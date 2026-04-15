import { useState } from 'react';
import type { CardImageProps } from '../types';

export function CardImage({ editionId, edid, alt, className = '', loading = 'lazy' }: CardImageProps) {
  const [imageError, setImageError] = useState(false);

  const imageUrl = `/images/${editionId}/${edid}.png`;
  const fallbackSvg = `data:image/svg+xml,${encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="200" height="280" viewBox="0 0 200 280">
      <rect width="200" height="280" fill="#1a1a2e"/>
      <rect x="10" y="10" width="180" height="260" fill="#16213e" rx="8"/>
      <text x="100" y="140" text-anchor="middle" fill="#64748b" font-family="sans-serif" font-size="14">Imagen no</text>
      <text x="100" y="160" text-anchor="middle" fill="#64748b" font-family="sans-serif" font-size="14">disponible</text>
    </svg>
  `)}`;

  const handleError = () => {
    setImageError(true);
  };

  return (
    <img
      src={imageError ? fallbackSvg : imageUrl}
      alt={alt}
      className={className}
      loading={loading}
      onError={handleError}
    />
  );
}
