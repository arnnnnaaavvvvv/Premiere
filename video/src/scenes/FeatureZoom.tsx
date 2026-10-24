import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { captionFont, headlineFont, theme } from "../theme";

interface FeatureZoomProps {
  headline: string;
  detail: string;
  mediaPath?: string;
}

export const FeatureZoom: React.FC<FeatureZoomProps> = ({
  headline,
  detail,
  mediaPath = "",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const zoomSpring = spring({ frame, fps, config: theme.spring.smooth });
  const zoomScale = interpolate(zoomSpring, [0, 1], [1.0, 1.25]);

  return (
    <AbsoluteFill
      style={{
        background: theme.colors.background,
        overflow: "hidden",
        display: "flex",
      }}
    >
      {/* Zoomed Background Media with Macro Blur */}
      {mediaPath && (
        <AbsoluteFill
          style={{
            transform: `scale(${zoomScale})`,
            transformOrigin: "center center",
            filter: "brightness(0.6) contrast(1.1)",
          }}
        >
          <Img src={mediaPath} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
      )}

      {/* Hero Feature Spotlight Card */}
      <div
        style={{
          position: "absolute",
          left: 140,
          bottom: 120,
          padding: "40px 48px",
          borderRadius: 20,
          background: "rgba(13, 15, 20, 0.88)",
          backdropFilter: "blur(24px)",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          boxShadow: "0 25px 60px rgba(0,0,0,0.8), 0 0 40px rgba(59,130,246,0.2)",
          maxWidth: 680,
        }}
      >
        <div
          style={{
            fontFamily: captionFont,
            fontSize: 14,
            fontWeight: 700,
            color: theme.colors.accent,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            marginBottom: 12,
          }}
        >
          CORE CAPABILITY
        </div>
        <h3
          style={{
            fontFamily: headlineFont,
            fontSize: 72,
            lineHeight: 1,
            color: theme.colors.white,
            margin: "0 0 16px 0",
            textTransform: "uppercase",
          }}
        >
          {headline}
        </h3>
        <p
          style={{
            fontFamily: captionFont,
            fontSize: 20,
            lineHeight: 1.5,
            color: theme.colors.textMuted,
            margin: 0,
          }}
        >
          {detail}
        </p>
      </div>
    </AbsoluteFill>
  );
};
