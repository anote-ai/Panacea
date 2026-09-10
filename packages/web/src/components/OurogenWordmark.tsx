interface Props {
  /** Applied to the card wrapper — use for margin/spacing (e.g. "mb-4"). */
  className?: string;
  /** Height of the logo icon itself. */
  imgHeight?: string;
}

/** The full "Ourogen" wordmark (icon + text). Shown on a light card — even
 * in dark mode — rather than directly on the page background, since the
 * icon PNG is solid black. */
export default function OurogenWordmark({ className = "", imgHeight = "h-10" }: Props) {
  return (
    <div className={`inline-flex items-center gap-2.5 bg-white rounded-xl px-4 py-2.5 shadow-sm border border-gray-200 ${className}`}>
      <img src="/ourogen-icon-black.png" alt="" className={`${imgHeight} w-auto`} />
      <span className="text-xl font-semibold tracking-tight text-gray-900">Ourogen</span>
    </div>
  );
}
