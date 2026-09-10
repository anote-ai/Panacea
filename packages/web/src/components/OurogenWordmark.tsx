import OurogenLogo from "./OurogenLogo";

interface Props {
  /** Applied to the card wrapper — use for margin/spacing (e.g. "mb-4"). */
  className?: string;
  /** Height of the logo icon itself. */
  imgHeight?: string;
}

/** Theme-aware mark and wordmark, matching the Ourogen site navigation. */
export default function OurogenWordmark({ className = "", imgHeight = "h-10" }: Props) {
  return (
    <div className={`inline-flex items-center gap-2.5 ${className}`}>
      <OurogenLogo className={`${imgHeight} w-auto`} />
      <span className="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">Ourogen</span>
    </div>
  );
}
