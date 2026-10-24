import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { captionFont, headlineFont, theme } from "../theme";

interface TitleRevealProps {
  productName: string;
  tagline: string;
  brandColor?: string;
}

export const TitleReveal: React.FC<TitleRevealProps> = ({
  productName,
  tagline,
  brandColor = theme.colors.primary,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: theme.spring.snappy,
  });

  const scale = interpolate(titleSpring, [0, 1], [0.88, 1.0]);
  const opacity = interpolate(titleSpring, [0, 0.5, 1], [0, 0.8, 1]);
  const taglineOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateRight: "clamp" });
  const taglineY = interpolate(frame, [15, 30], [20, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: theme.colors.background,
        textAlign: "center",
      }}
    >
      {/* Category Pill Tag */}
      <div
        style={{
          fontFamily: captionFont,
          fontSize: 18,
          fontWeight: 600,
          color: brandColor,
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          marginBottom: 24,
          padding: "8px 20px",
          background: "rgba(59, 130, 246, 0.08)",
          borderRadius: 999,
          border: "1px solid rgba(59, 130, 246, 0.2)",
        }}
      >
        INTRODUCING
      </div>

      {/* Hero Headline (Bebas Neue) */}
      <h1
        style={{
          fontFamily: headlineFont,
          fontSize: 160,
          lineHeight: 0.95,
          color: theme.colors.white,
          letterSpacing: "-0.02em",
          margin: 0,
          textTransform: "uppercase",
          transform: `scale(${scale})`,
          opacity,
          textShadow: "0 0 60px rgba(255,255,255,0.2)",
        }}
      >
        {productName}
      </h1>

      {/* Caption Tagline (Inter) */}
      <p
        style={{
          fontFamily: captionFont,
          fontSize: 32,
          color: theme.colors.textMuted,
          maxWidth: 900,
          marginTop: 28,
          opacity: taglineOpacity,
          transform: `translateY(${taglineY}px)`,
          letterSpacing: "0.04em",
          textTransform: "uppercase",
        }}
      >
        {tagline}
      </p>
    </AbsoluteFill>
  );
};
