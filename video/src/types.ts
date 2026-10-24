export type SceneType =
  | "TitleReveal"
  | "DeviceShowcase"
  | "FeatureZoom"
  | "StatCounter"
  | "KineticText"
  | "Outro";

export type TransitionType =
  | "none"
  | "push"
  | "zoom-through"
  | "mask-wipe"
  | "blur-dissolve"
  | "glitch-flash"
  | "shared-element-morph";

export interface SceneConfig {
  sceneId: string;
  sceneType: SceneType;
  headline: string;
  caption: string;
  durationFrames: number;
  transitionIn: TransitionType;
  targetRoute?: string;
  mediaPath?: string;
  props?: Record<string, any>;
}

export interface VideoTheme {
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  surfaceColor: string;
}

export interface VideoProps {
  productName: string;
  tagline: string;
  theme?: Partial<VideoTheme>;
  audioUrl?: string;
  scenes: SceneConfig[];
}
