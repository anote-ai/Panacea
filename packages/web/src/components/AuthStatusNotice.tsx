import { getAuthStatusNotice, HealthFetchState, ServiceHealth } from "../lib/productReadiness";

interface Props {
  health: ServiceHealth | null;
  healthState: HealthFetchState;
}

export default function AuthStatusNotice({ health, healthState }: Props) {
  const notice = getAuthStatusNotice(healthState, health);

  if (!notice) return null;

  const isError = notice.tone === "error";

  return (
    <div
      className={`mb-4 rounded-xl border px-4 py-3 text-sm ${
        isError
          ? "border-red-200 bg-red-50 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-200"
          : "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100"
      }`}
    >
      <p className="font-medium">{notice.title}</p>
      <p className="mt-1 text-xs opacity-90">{notice.detail}</p>
    </div>
  );
}
