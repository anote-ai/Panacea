import { useTheme } from "../App";

interface Props {
  className?: string;
}

/** The Ourogen ring-arrow icon on its own (no wordmark text) — used in the
 * small square slots (sidebar, navbar) that sit next to their own
 * separately-set label text. It's a solid black or solid white mark, so it
 * swaps variant with the theme: white on dark backgrounds, black on light
 * backgrounds. */
export default function OurogenLogo({ className = "w-8 h-8" }: Props) {
  const { dark } = useTheme();
  const src = dark ? "/ourogen-icon-white.png" : "/ourogen-icon-black.png";
  return <img src={src} alt="Ourogen" className={`${className} object-contain`} />;
}
