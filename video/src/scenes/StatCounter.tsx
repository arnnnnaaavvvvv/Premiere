import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { captionFont, headlineFont, theme } from "../theme";

interface StatCounterProps {
  metricValue?: string;
  metricLabel?: string;
}

export const StatCounter: React.FC<StatCounterProps> = ({
  metricValue = "10X",
  metricLabel = "FASTER TIME TO MARKET",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const numSpring = spring({
    frame,
    fps,
    config: theme.spring.snappy,
  });

  const scale = interpolate(numSpring, [0, 1], [0.8, 1.0]);
  const opacity = interpolate(numSpring, [0, 0.4, 1], [0, 0.9, 1]);
  const glow = interpolate(frame, [0, 30], [20, 80], { extrapolateRight: "clamp" });

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
      {/* Giant Numerals in Bebas Neue */}
      <div
        style={{
          fontFamily: headlineFont,
          fontSize: 260,
          lineHeight: 0.85,
          color: theme.colors.white,
          letterSpacing: "-0.04em",
          transform: `scale(${scale})`,
          opacity,
          textShadow: `0 0 ${glow}px rgba(59, 130, 246, 0.5)`,
        }}
      >
        {metricValue}
      </div>

      {/* Metric Context in Bebas Neue */}
      <div
        style={{
          fontFamily: headlineFont,
          fontSize: 64,
          color: theme.colors.primary,
          letterSpacing: "0.08em",
          marginTop: 20,
          textTransform: "uppercase",
        }}
      >
        {metricLabel}
      </div>

      {/* Subtitle Caption */}
      <p
        style={{
          fontFamily: captionFont,
          fontSize: 20,
          color: theme.colors.textMuted,
          marginTop: 16,
        }}
      >
        Benchmarked across high-concurrency production workloads
      </p>
    </AbsoluteFill>
  );
};
