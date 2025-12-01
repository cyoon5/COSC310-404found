export function getBanRemainingSeconds(banExpiresAt: number | null): number {
  if (!banExpiresAt) return 0;
  const now = Date.now() / 1000;
  return Math.max(0, banExpiresAt - now);
}

export function formatDuration(seconds: number): string {
  if (seconds <= 0) return "0 seconds";

  const days = Math.floor(seconds / 86400);
  seconds %= 86400;

  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;

  const minutes = Math.floor(seconds / 60);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes} minutes`;
}
