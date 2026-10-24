import { loadFont as loadBebasNeue } from "@remotion/google-fonts/BebasNeue";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// Initialize font loaders
export const { fontFamily: headlineFont } = loadBebasNeue();
export const { fontFamily: captionFont } = loadInter();

export const theme = {
  colors: {
    background: "#050505",
    surface: "#0D0F14",
    cardBorder: "rgba(255, 255, 255, 0.08)",
    primary: "#3B82F6",
    accent: "#60A5FA",
    textMuted: "#94A3B8",
    white: "#FFFFFF",
  },
  spring: {
    snappy: { damping: 16, stiffness: 150, mass: 0.8 },
    smooth: { damping: 20, stiffness: 120, mass: 1.0 },
    gentle: { damping: 24, stiffness: 90, mass: 1.2 },
  },
  easing: {
    appleOut: [0.16, 1.0, 0.3, 1.0],
  },
  margins: {
    safeTop: 100,
    safeBottom: 100,
    safeLeft: 120,
    safeRight: 120,
  },
};
