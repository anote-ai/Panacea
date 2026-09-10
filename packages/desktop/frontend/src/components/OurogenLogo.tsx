import { useTheme } from "../App";

export default function OurogenLogo({ className = "w-8 h-8" }: { className?: string }) {
  const { dark } = useTheme();
  return <img src={`./ourogen-icon-${dark ? "white" : "black"}.png`} alt="Ourogen" className={`${className} object-contain mix-blend-multiply dark:mix-blend-screen`} />;
}
