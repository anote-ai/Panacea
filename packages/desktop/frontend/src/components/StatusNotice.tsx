import { StatusNotice as StatusNoticeType } from "../lib/productReadiness";

interface Props {
  notice: StatusNoticeType;
  className?: string;
}

export default function StatusNotice({ notice, className = "" }: Props) {
  const isError = notice.tone === "error";

  return (
    <div
      className={`rounded-2xl border px-4 py-3 text-sm ${
        isError
          ? "border-red-200 bg-red-50 text-red-700 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-200"
          : "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100"
      } ${className}`}
    >
      <p className="font-medium">{notice.title}</p>
      <p className="mt-1 text-xs opacity-90">{notice.detail}</p>
    </div>
  );
}
