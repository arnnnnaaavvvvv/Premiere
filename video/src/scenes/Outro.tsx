import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { captionFont, headlineFont, theme } from "../theme";

interface OutroProps {
  productName: string;
  ctaText?: string;
  brandColor?: string;
}

export const Outro: React.FC<OutroProps> = ({
  productName,
  ctaText = "START BUILDING TODAY",
  brandColor = theme.colors.primary,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoSpring = spring({ frame, fps, config: theme.spring.snappy });
  const scale = interpolate(logoSpring, [0, 1], [0.9, 1.0]);
  const opacity = interpolate(logoSpring, [0, 0.4, 1], [0, 0.8, 1]);

  return (
    <AbsoluteFill
      style={{
        background: theme.colors.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
      }}
    >
      {/* Brand Name Headline */}
      <h1
        style={{
          fontFamily: headlineFont,
          fontSize: 150,
          color: theme.colors.white,
          letterSpacing: "-0.02em",
          margin: 0,
          textTransform: "uppercase",
          transform: `scale(${scale})`,
          opacity,
          textShadow: `0 0 70px ${brandColor}`,
        }}
      >
        {productName}
      </h1>

      {/* Primary Action Button */}
      <div
        style={{
          marginTop: 40,
          padding: "18px 48px",
          background: brandColor,
          borderRadius: 999,
          color: "#FFFFFF",
          fontFamily: headlineFont,
          fontSize: 36,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          boxShadow: `0 0 50px ${brandColor}88`,
        }}
      >
        {ctaText}
      </div>

      {/* GitHub Star Pill Badge */}
      <div
        style={{
          marginTop: 28,
          fontFamily: captionFont,
          fontSize: 16,
          color: theme.colors.textMuted,
          letterSpacing: "0.08em",
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span>★ STAR ON GITHUB</span>
        <span>•</span>
        <span>OPEN SOURCE</span>
      </div>
    </AbsoluteFill>
  );
};
