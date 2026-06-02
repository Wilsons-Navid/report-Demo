"use client";

import React from "react";

// Types
interface GlassEffectProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  href?: string;
  target?: string;
}

interface DockIcon {
  src: string;
  alt: string;
  onClick?: () => void;
}

// Glass Effect Wrapper Component
export const GlassEffect: React.FC<GlassEffectProps> = ({
  children,
  className = "",
  style = {},
  href,
  target = "_blank",
}) => {
  const glassStyle: React.CSSProperties = {
    transitionTimingFunction: "cubic-bezier(0.175, 0.885, 0.32, 2.2)",
    ...style,
  };

  const content = (
    <div
      className={`group relative isolate flex overflow-hidden font-semibold text-white transition-all duration-500 ${className}`}
      style={glassStyle}
    >
      {/* frosted backdrop — the real glass, matched to .glass-card */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-0 rounded-[inherit]"
        style={{
          background: "rgba(255, 255, 255, 0.07)",
          backdropFilter: "blur(20px) saturate(1.4)",
          WebkitBackdropFilter: "blur(20px) saturate(1.4)",
        }}
      />
      {/* refractive sheen — a soft diagonal light-catch that brightens on hover */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-10 rounded-[inherit] opacity-80 transition-opacity duration-500 group-hover:opacity-100"
        style={{
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.05) 28%, transparent 52%)",
        }}
      />
      {/* crisp glass edges + depth shadow */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 z-20 rounded-[inherit]"
        style={{
          border: "1px solid rgba(255, 255, 255, 0.16)",
          boxShadow:
            "inset 0 1px 0 rgba(255,255,255,0.35), inset 0 -1px 0 rgba(255,255,255,0.06), 0 24px 60px -24px rgba(0,0,0,0.6)",
        }}
      />

      {/* Content */}
      <div className="relative z-30">{children}</div>
    </div>
  );

  return href ? (
    <a href={href} target={target} rel="noopener noreferrer" className="block">
      {content}
    </a>
  ) : (
    content
  );
};

// Dock Component
export const GlassDock: React.FC<{ icons: DockIcon[]; href?: string }> = ({
  icons,
  href,
}) => (
  <GlassEffect
    href={href}
    className="rounded-3xl p-3 hover:p-4 hover:rounded-[2rem]"
  >
    <div className="flex items-center justify-center gap-2 rounded-3xl p-3 py-0 px-0.5 overflow-hidden">
      {icons.map((icon, index) => (
        <img
          key={index}
          src={icon.src}
          alt={icon.alt}
          className="w-14 h-14 transition-all duration-700 hover:scale-110 cursor-pointer"
          style={{
            transformOrigin: "center center",
            transitionTimingFunction: "cubic-bezier(0.175, 0.885, 0.32, 2.2)",
          }}
          onClick={icon.onClick}
        />
      ))}
    </div>
  </GlassEffect>
);

// Button Component
export const GlassButton: React.FC<{ children: React.ReactNode; href?: string; className?: string }> = ({
  children,
  href,
  className = "",
}) => (
  <GlassEffect
    href={href}
    className={`rounded-2xl px-8 py-4 hover:px-9 hover:py-[1.15rem] hover:rounded-3xl overflow-hidden ${className}`}
  >
    <div
      className="transition-all duration-700 hover:scale-95"
      style={{
        transitionTimingFunction: "cubic-bezier(0.175, 0.885, 0.32, 2.2)",
      }}
    >
      {children}
    </div>
  </GlassEffect>
);

// SVG Filter Component
export const GlassFilter: React.FC = () => (
  <svg style={{ display: "none" }} aria-hidden="true">
    <filter
      id="glass-distortion"
      x="0%"
      y="0%"
      width="100%"
      height="100%"
      filterUnits="objectBoundingBox"
    >
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.001 0.005"
        numOctaves="1"
        seed="17"
        result="turbulence"
      />
      <feComponentTransfer in="turbulence" result="mapped">
        <feFuncR type="gamma" amplitude="1" exponent="10" offset="0.5" />
        <feFuncG type="gamma" amplitude="0" exponent="1" offset="0" />
        <feFuncB type="gamma" amplitude="0" exponent="1" offset="0.5" />
      </feComponentTransfer>
      <feGaussianBlur in="turbulence" stdDeviation="3" result="softMap" />
      <feSpecularLighting
        in="softMap"
        surfaceScale="5"
        specularConstant="1"
        specularExponent="100"
        lightingColor="white"
        result="specLight"
      >
        <fePointLight x="-200" y="-200" z="300" />
      </feSpecularLighting>
      <feComposite
        in="specLight"
        operator="arithmetic"
        k1="0"
        k2="1"
        k3="1"
        k4="0"
        result="litImage"
      />
      <feDisplacementMap
        in="SourceGraphic"
        in2="softMap"
        scale="200"
        xChannelSelector="R"
        yChannelSelector="G"
      />
    </filter>
  </svg>
);

// Main demo component (kept from source)
export const Component = () => {
  const dockIcons: DockIcon[] = [
    {
      src: "https://parsefiles.back4app.com/JPaQcFfEEQ1ePBxbf6wvzkPMEqKYHhPYv8boI1Rc/a13d1acfd046f503f987c1c95af582c8_low_res_Claude.png",
      alt: "Claude",
    },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center font-light relative overflow-hidden w-full">
      <GlassFilter />
      <div className="flex flex-col gap-6 items-center justify-center w-full">
        <GlassDock icons={dockIcons} />
        <GlassButton>
          <div className="text-xl text-white">
            <p>How can i help you today?</p>
          </div>
        </GlassButton>
      </div>
    </div>
  );
};
