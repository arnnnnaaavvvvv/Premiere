import React from "react";
import { Img } from "remotion";

interface DeviceFrameProps {
  mediaSrc: string;
  type?: "laptop" | "mobile";
  tiltProgress?: number;
}

export const DeviceFrame: React.FC<DeviceFrameProps> = ({
  mediaSrc,
  type = "laptop",
  tiltProgress = 0,
}) => {
  const rotateX = 6 - tiltProgress * 4;
  const rotateY = -8 + tiltProgress * 6;

  return (
    <div
      style={{
        width: 1400,
        height: 820,
        perspective: 1400,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
          transformStyle: "preserve-3d",
          borderRadius: 16,
          background: "#1E222B",
          border: "2px solid rgba(255, 255, 255, 0.12)",
          boxShadow: "0 35px 70px -15px rgba(0,0,0,0.9), 0 0 100px rgba(59,130,246,0.15)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* macOS Style Traffic Light Window Header */}
        <div
          style={{
            height: 38,
            background: "#12141A",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: 8,
          }}
        >
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F56" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#27C93F" }} />
          <div
            style={{
              marginLeft: "auto",
              marginRight: "auto",
              fontSize: 12,
              color: "#64748B",
              fontFamily: "Inter, sans-serif",
            }}
          >
            reelforge.live
          </div>
        </div>

        {/* Live captured screen contents */}
        <div style={{ flex: 1, position: "relative", overflow: "hidden", background: "#050505" }}>
          {mediaSrc ? (
            <Img
              src={mediaSrc}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                objectPosition: "top center",
              }}
            />
          ) : (
            <div style={{ width: "100%", height: "100%", background: "#0B0F19" }} />
          )}
        </div>
      </div>
    </div>
  );
};
