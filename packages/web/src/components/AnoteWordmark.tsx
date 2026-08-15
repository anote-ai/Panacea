interface Props {
  /** Applied to the card wrapper — use for margin/spacing (e.g. "mb-4"). */
  className?: string;
  /** Height of the logo image itself. */
  imgHeight?: string;
}

/** The full "Anote" wordmark (icon + text). Its text is dark navy, so it's
 * always shown on a light card — even in dark mode — rather than directly
 * on the page background. */
export default function AnoteWordmark({ className = "", imgHeight = "h-10" }: Props) {
  return (
    <div className={`inline-flex items-center bg-white rounded-xl px-4 py-2.5 shadow-sm border border-gray-200 ${className}`}>
      <img src="/anote-logo.png" alt="Anote" className={`${imgHeight} w-auto`} />
    </div>
  );
}
