import React from "react";
import { AbsoluteFill } from "remotion";

export const FilmOverlay: React.FC<{ glowColor?: string }> = ({
  glowColor = "rgba(59, 130, 246, 0.12)",
}) => {
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* 1. Atmospheric Diffuse Ambient Radial Glow */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 1200,
          height: 800,
          background: `radial-gradient(circle, ${glowColor} 0%, rgba(5,5,5,0) 70%)`,
          filter: "blur(60px)",
        }}
      />

      {/* 2. Cinema Edge Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, transparent 40%, rgba(0,0,0,0.85) 100%)",
        }}
      />

      {/* 3. Subtle Film Grain Micro-Texture */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.035,
          backgroundImage: "repeating-radial-gradient(#fff 0 0.0001%, #000 0 0.0002%)",
          mixBlendMode: "overlay",
        }}
      />
    </AbsoluteFill>
  );
};
