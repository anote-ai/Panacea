import { Image } from "react-native";

export default function OurogenLogo({ size = 32, dark = false }: { size?: number; dark?: boolean }) {
  return <Image source={dark ? require("../../assets/ourogen-icon-white.png") : require("../../assets/ourogen-icon-black.png")}
    style={{ width: size, height: size }} resizeMode="contain" accessibilityLabel="Ourogen" />;
}
