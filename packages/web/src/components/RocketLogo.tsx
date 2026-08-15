interface Props {
  className?: string;
}

/** The Anote rocket icon on its own (no wordmark text) — used in the small
 * square slots (sidebar, navbar, favicon-adjacent spots) that sit next to
 * their own separately-set label text. Its colors read fine on both light
 * and dark backgrounds, so no theme-specific handling is needed. */
export default function RocketLogo({ className = "w-8 h-8" }: Props) {
  return <img src="/anote-icon.png" alt="Anote" className={`${className} object-contain`} />;
}
