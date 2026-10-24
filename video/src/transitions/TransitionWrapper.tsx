import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { TransitionType } from "../types";

interface TransitionWrapperProps {
  transition: TransitionType;
  children: React.ReactNode;
}

export const TransitionWrapper: React.FC<TransitionWrapperProps> = ({
  transition,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth entrance spring
  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 140, mass: 1 },
  });

  if (transition === "push") {
    const translateX = interpolate(enterSpring, [0, 1], [400, 0]);
    const opacity = interpolate(enterSpring, [0, 0.4, 1], [0, 0.8, 1]);
    return (
      <AbsoluteFill style={{ transform: `translateX(${translateX}px)`, opacity }}>
        {children}
      </AbsoluteFill>
    );
  }

  if (transition === "zoom-through") {
    const scale = interpolate(enterSpring, [0, 1], [0.85, 1.0]);
    const opacity = interpolate(enterSpring, [0, 0.5, 1], [0, 0.9, 1]);
    return (
      <AbsoluteFill style={{ transform: `scale(${scale})`, opacity }}>
        {children}
      </AbsoluteFill>
    );
  }

  if (transition === "mask-wipe") {
    const wipe = interpolate(frame, [0, 14], [0, 100], { extrapolateRight: "clamp" });
    return (
      <AbsoluteFill style={{ clipPath: `polygon(0 0, ${wipe}% 0, ${wipe}% 100%, 0 100%)` }}>
        {children}
      </AbsoluteFill>
    );
  }

  if (transition === "blur-dissolve") {
    const blur = interpolate(frame, [0, 12], [20, 0], { extrapolateRight: "clamp" });
    const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
    return (
      <AbsoluteFill style={{ filter: `blur(${blur}px)`, opacity }}>
        {children}
      </AbsoluteFill>
    );
  }

  if (transition === "glitch-flash") {
    const flash = frame < 3 ? 1.4 : 1.0;
    const offset = frame === 1 ? 8 : 0;
    return (
      <AbsoluteFill style={{ filter: `brightness(${flash})`, transform: `translateX(${offset}px)` }}>
        {children}
      </AbsoluteFill>
    );
  }

  if (transition === "shared-element-morph") {
    const scale = interpolate(enterSpring, [0, 1], [0.95, 1.0]);
    const opacity = interpolate(enterSpring, [0, 0.3, 1], [0, 0.7, 1]);
    return (
      <AbsoluteFill style={{ transform: `scale(${scale})`, opacity }}>
        {children}
      </AbsoluteFill>
    );
  }

  // Default: clean cut
  return <AbsoluteFill>{children}</AbsoluteFill>;
};
