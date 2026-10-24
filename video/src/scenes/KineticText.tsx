import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { headlineFont, theme } from "../theme";

interface KineticTextProps {
  words?: string[];
}

export const KineticText: React.FC<KineticTextProps> = ({
  words = ["BUILT.", "FOR.", "SPEED."],
}) => {
  const frame = useCurrentFrame();

  // Switch words every 18 frames
  const framesPerWord = 18;
  const wordIndex = Math.min(Math.floor(frame / framesPerWord), words.length - 1);
  const activeWord = words[wordIndex];

  // Brief flash on each transition
  const isFlash = frame % framesPerWord < 2;

  return (
    <AbsoluteFill
      style={{
        background: isFlash ? "#FFFFFF" : theme.colors.background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
      }}
    >
      <h1
        style={{
          fontFamily: headlineFont,
          fontSize: 220,
          lineHeight: 0.9,
          color: isFlash ? "#050505" : theme.colors.white,
          letterSpacing: "-0.02em",
          margin: 0,
          textTransform: "uppercase",
          textShadow: isFlash ? "none" : "0 0 80px rgba(59,130,246,0.4)",
        }}
      >
        {activeWord}
      </h1>
    </AbsoluteFill>
  );
};
