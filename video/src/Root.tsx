import React from "react";
import { Composition } from "remotion";
import { LaunchVideo } from "./Composition";
import { VideoProps } from "./types";

const defaultProps: VideoProps = {
  productName: "PREMIERE",
  tagline: "AUTONOMOUS MNC-GRADE LAUNCH FILMS IN MINUTES",
  scenes: [
    {
      sceneId: "scene-1",
      sceneType: "TitleReveal",
      headline: "PREMIERE",
      caption: "AUTONOMOUS MNC-GRADE LAUNCH FILMS IN MINUTES",
      durationFrames: 75,
      transitionIn: "none",
    },
    {
      sceneId: "scene-2",
      sceneType: "DeviceShowcase",
      headline: "PRECISION MOTION",
      caption: "High velocity animations aligned to musical beats",
      durationFrames: 90,
      transitionIn: "zoom-through",
    },
    {
      sceneId: "scene-3",
      sceneType: "StatCounter",
      headline: "10X FASTER",
      caption: "Zero-touch turnaround from code to film",
      durationFrames: 75,
      transitionIn: "mask-wipe",
      props: { metric_value: "10X", metric_label: "FASTER LAUNCHES" },
    },
    {
      sceneId: "scene-4",
      sceneType: "KineticText",
      headline: "BUILT. FOR. SPEED.",
      caption: "",
      durationFrames: 60,
      transitionIn: "glitch-flash",
      props: { words: ["BUILT.", "FOR.", "SCALE."] },
    },
    {
      sceneId: "scene-5",
      sceneType: "Outro",
      headline: "START BUILDING TODAY",
      caption: "Get started with Premiere",
      durationFrames: 90,
      transitionIn: "blur-dissolve",
    },
  ],
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PremiereComposition"
        component={LaunchVideo}
        durationInFrames={390}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
    </>
  );
};
