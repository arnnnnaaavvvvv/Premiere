import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { DeviceFrame } from "../components/DeviceFrame";
import { captionFont, headlineFont, theme } from "../theme";

interface DeviceShowcaseProps {
  headline: string;
  caption: string;
  mediaPath?: string;
}

export const DeviceShowcase: React.FC<DeviceShowcaseProps> = ({
  headline,
  caption,
  mediaPath = "",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = frame / durationInFrames;
  const headerOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const translateY = interpolate(frame, [0, 20], [30, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: theme.colors.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 40px 20px 40px",
      }}
    >
      {/* Scene Header */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 36,
          opacity: headerOpacity,
          transform: `translateY(${translateY}px)`,
        }}
      >
        <h2
          style={{
            fontFamily: headlineFont,
            fontSize: 90,
            lineHeight: 1,
            color: theme.colors.white,
            margin: 0,
            textTransform: "uppercase",
            letterSpacing: "-0.01em",
          }}
        >
          {headline}
        </h2>
        <p
          style={{
            fontFamily: captionFont,
            fontSize: 22,
            color: theme.colors.textMuted,
            margin: "10px 0 0 0",
          }}
        >
          {caption}
        </p>
      </div>

      {/* 3D Floating Laptop Chassis */}
      <DeviceFrame mediaSrc={mediaPath} tiltProgress={progress} />
    </AbsoluteFill>
  );
};
