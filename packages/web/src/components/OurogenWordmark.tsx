interface Props {
  /** Applied to the card wrapper — use for margin/spacing (e.g. "mb-4"). */
  className?: string;
  /** Height of the wordmark image itself. */
  imgHeight?: string;
}

/** The full "Ourogen" wordmark (icon + text, as one image). Shown on a
 * light card — even in dark mode — rather than directly on the page
 * background, since the wordmark PNG is solid black. */
export default function OurogenWordmark({ className = "", imgHeight = "h-8" }: Props) {
  return (
    <div className={`inline-flex items-center bg-white rounded-xl px-4 py-2.5 shadow-sm border border-gray-200 ${className}`}>
      <img src="/ourogen-wordmark-black.png" alt="Ourogen" className={`${imgHeight} w-auto`} />
    </div>
  );
}
