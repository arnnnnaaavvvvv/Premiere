import React from "react";
import { AbsoluteFill, Audio, Series } from "remotion";
import { FilmOverlay } from "./components/FilmOverlay";
import { DeviceShowcase } from "./scenes/DeviceShowcase";
import { FeatureZoom } from "./scenes/FeatureZoom";
import { KineticText } from "./scenes/KineticText";
import { Outro } from "./scenes/Outro";
import { StatCounter } from "./scenes/StatCounter";
import { TitleReveal } from "./scenes/TitleReveal";
import { TransitionWrapper } from "./transitions/TransitionWrapper";
import { VideoProps } from "./types";

export const LaunchVideo: React.FC<VideoProps> = ({
  productName,
  tagline,
  theme: customTheme,
  audioUrl,
  scenes,
}) => {
  const brandColor = customTheme?.primaryColor || "#3B82F6";

  return (
    <AbsoluteFill style={{ backgroundColor: "#050505" }}>
      {/* 1. Master Audio Track with Ducking */}
      {audioUrl && <Audio src={audioUrl} volume={0.8} />}

      {/* 2. Beat-Aligned Sequential Scenes */}
      <Series>
        {scenes.map((scene) => {
          let sceneContent = null;

          if (scene.sceneType === "TitleReveal") {
            sceneContent = (
              <TitleReveal
                productName={productName}
                tagline={tagline}
                brandColor={brandColor}
              />
            );
          } else if (scene.sceneType === "DeviceShowcase") {
            sceneContent = (
              <DeviceShowcase
                headline={scene.headline}
                caption={scene.caption}
                mediaPath={scene.mediaPath}
              />
            );
          } else if (scene.sceneType === "FeatureZoom") {
            sceneContent = (
              <FeatureZoom
                headline={scene.headline}
                detail={scene.caption}
                mediaPath={scene.mediaPath}
              />
            );
          } else if (scene.sceneType === "StatCounter") {
            sceneContent = (
              <StatCounter
                metricValue={scene.props?.metric_value || "10X"}
                metricLabel={scene.props?.metric_label || scene.headline}
              />
            );
          } else if (scene.sceneType === "KineticText") {
            sceneContent = (
              <KineticText words={scene.props?.words || ["BUILT.", "FOR.", "SCALE."]} />
            );
          } else if (scene.sceneType === "Outro") {
            sceneContent = (
              <Outro
                productName={productName}
                ctaText={scene.props?.cta_text || "START BUILDING TODAY"}
                brandColor={brandColor}
              />
            );
          }

          return (
            <Series.Sequence
              key={scene.sceneId}
              durationInFrames={scene.durationFrames}
            >
              <TransitionWrapper transition={scene.transitionIn}>
                {sceneContent}
              </TransitionWrapper>
            </Series.Sequence>
          );
        })}
      </Series>

      {/* 3. Subtle Film Grain, Vignette, and Glow Overlay */}
      <FilmOverlay glowColor={`${brandColor}22`} />
    </AbsoluteFill>
  );
};
