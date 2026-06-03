"use client";
import { useState, useEffect, useRef } from "react";
import { ArrowRight, Link, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TimelineItem {
  id: number;
  title: string;
  date: string;
  content: string;
  category: string;
  icon: React.ElementType;
  relatedIds: number[];
  status: "completed" | "in-progress" | "pending";
  energy: number;
  color?: string;
  image?: string;
}

interface RadialOrbitalTimelineProps {
  timelineData: TimelineItem[];
}

export default function RadialOrbitalTimeline({
  timelineData,
}: RadialOrbitalTimelineProps) {
  const [expandedItems, setExpandedItems] = useState<Record<number, boolean>>({});
  const [rotationAngle, setRotationAngle] = useState<number>(0);
  const [autoRotate, setAutoRotate] = useState<boolean>(true);
  const [pulseEffect, setPulseEffect] = useState<Record<number, boolean>>({});
  const [activeNodeId, setActiveNodeId] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const orbitRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<Record<number, HTMLDivElement | null>>({});

  // viewMode and centerOffset are fixed for this orbital layout.
  const viewMode = "orbital";
  const centerOffset = { x: 0, y: 0 };

  // Respect reduced-motion: stop the perpetual rotation if requested.
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setAutoRotate(false);
    }
  }, []);

  const handleContainerClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === containerRef.current || e.target === orbitRef.current) {
      setExpandedItems({});
      setActiveNodeId(null);
      setPulseEffect({});
      setAutoRotate(true);
    }
  };

  const toggleItem = (id: number) => {
    setExpandedItems((prev) => {
      const newState = { ...prev };
      Object.keys(newState).forEach((key) => {
        if (parseInt(key) !== id) newState[parseInt(key)] = false;
      });

      newState[id] = !prev[id];

      if (!prev[id]) {
        setActiveNodeId(id);
        setAutoRotate(false);

        const relatedItems = getRelatedItems(id);
        const newPulseEffect: Record<number, boolean> = {};
        relatedItems.forEach((relId) => {
          newPulseEffect[relId] = true;
        });
        setPulseEffect(newPulseEffect);

        centerViewOnNode(id);
      } else {
        setActiveNodeId(null);
        setAutoRotate(true);
        setPulseEffect({});
      }

      return newState;
    });
  };

  useEffect(() => {
    let rotationTimer: ReturnType<typeof setInterval> | undefined;

    if (autoRotate && viewMode === "orbital") {
      rotationTimer = setInterval(() => {
        setRotationAngle((prev) => {
          const newAngle = (prev + 0.1) % 360;
          return Number(newAngle.toFixed(3));
        });
      }, 50);
    }

    return () => {
      if (rotationTimer) clearInterval(rotationTimer);
    };
  }, [autoRotate, viewMode]);

  const centerViewOnNode = (nodeId: number) => {
    if (viewMode !== "orbital" || !nodeRefs.current[nodeId]) return;
    const nodeIndex = timelineData.findIndex((item) => item.id === nodeId);
    const totalNodes = timelineData.length;
    const targetAngle = (nodeIndex / totalNodes) * 360;
    setRotationAngle(270 - targetAngle);
  };

  const calculateNodePosition = (index: number, total: number) => {
    const angle = ((index / total) * 360 + rotationAngle) % 360;
    const radius = 200;
    const radian = (angle * Math.PI) / 180;

    const x = radius * Math.cos(radian) + centerOffset.x;
    const y = radius * Math.sin(radian) + centerOffset.y;

    const zIndex = Math.round(100 + 50 * Math.cos(radian));
    const opacity = Math.max(
      0.55,
      Math.min(1, 0.55 + 0.45 * ((1 + Math.sin(radian)) / 2)),
    );

    return { x, y, angle, zIndex, opacity };
  };

  const getRelatedItems = (itemId: number): number[] => {
    const currentItem = timelineData.find((item) => item.id === itemId);
    return currentItem ? currentItem.relatedIds : [];
  };

  const isRelatedToActive = (itemId: number): boolean => {
    if (!activeNodeId) return false;
    const relatedItems = getRelatedItems(activeNodeId);
    return relatedItems.includes(itemId);
  };

  const getStatusStyles = (status: TimelineItem["status"]): string => {
    switch (status) {
      case "completed":
        return "text-emerald-700 bg-emerald-50 border-emerald-200";
      case "in-progress":
        return "text-amber-800 bg-amber-50 border-amber-200";
      case "pending":
        return "text-slate-600 bg-slate-100 border-slate-200";
      default:
        return "text-slate-600 bg-slate-100 border-slate-200";
    }
  };

  return (
    <div
      className="relative flex h-[600px] w-full flex-col items-center justify-center overflow-hidden md:h-[680px]"
      ref={containerRef}
      onClick={handleContainerClick}
    >
      <div className="relative flex h-full w-full max-w-4xl items-center justify-center">
        <div
          className="absolute flex h-full w-full items-center justify-center"
          ref={orbitRef}
          style={{
            perspective: "1000px",
            transform: `translate(${centerOffset.x}px, ${centerOffset.y}px)`,
          }}
        >
          {/* center hub — Stripe blurple */}
          <div className="absolute z-10 flex h-16 w-16 items-center justify-center rounded-full animate-pulse" style={{ background: "radial-gradient(circle at 32% 28%, #8b7bff, #533afd 58%, #4434d4)", boxShadow: "0 10px 30px -8px rgba(83,58,253,.6)" }}>
            <div className="absolute h-20 w-20 animate-ping rounded-full opacity-60" style={{ border: "1px solid rgba(83,58,253,.35)" }} />
            <div className="absolute h-24 w-24 animate-ping rounded-full opacity-40" style={{ border: "1px solid rgba(83,58,253,.18)", animationDelay: "0.5s" }} />
            <div className="h-7 w-7 rounded-full bg-white/90" />
          </div>

          <div className="absolute h-96 w-96 rounded-full" style={{ border: "1px solid rgba(15,23,42,.08)" }} />

          {timelineData.map((item, index) => {
            const position = calculateNodePosition(index, timelineData.length);
            const isExpanded = expandedItems[item.id];
            const isRelated = isRelatedToActive(item.id);
            const isPulsing = pulseEffect[item.id];
            const Icon = item.icon;
            const accent = item.color ?? "var(--brand)";

            const nodeStyle = {
              transform: `translate(${position.x}px, ${position.y}px)`,
              zIndex: isExpanded ? 200 : position.zIndex,
              opacity: isExpanded ? 1 : position.opacity,
            };

            return (
              <div
                key={item.id}
                ref={(el) => {
                  nodeRefs.current[item.id] = el;
                }}
                className="absolute cursor-pointer transition-all duration-700"
                style={nodeStyle}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleItem(item.id);
                }}
              >
                <div
                  className={`absolute rounded-full -inset-1 ${isPulsing ? "animate-pulse duration-1000" : ""}`}
                  style={{
                    background: `radial-gradient(circle, ${accent}33 0%, transparent 70%)`,
                    width: `${item.energy * 0.5 + 40}px`,
                    height: `${item.energy * 0.5 + 40}px`,
                    left: `-${(item.energy * 0.5 + 40 - 40) / 2}px`,
                    top: `-${(item.energy * 0.5 + 40 - 40) / 2}px`,
                  }}
                />

                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300 ${isExpanded ? "scale-150" : ""}`}
                  style={{
                    background: isExpanded ? accent : isRelated ? `${accent}1f` : "#ffffff",
                    borderColor: isExpanded || isRelated ? accent : "rgba(15,23,42,0.14)",
                    color: isExpanded ? "#ffffff" : accent,
                    boxShadow: isExpanded ? `0 8px 20px ${accent}55` : "0 1px 3px rgba(15,23,42,0.12)",
                  }}
                >
                  <Icon size={16} />
                </div>

                <div
                  className={`absolute top-12 whitespace-nowrap text-xs font-semibold tracking-wide transition-all duration-300 ${
                    isExpanded ? "scale-110 text-slate-900" : "text-slate-500"
                  }`}
                >
                  {item.title}
                </div>

                {isExpanded && (
                  <Card className="absolute left-1/2 top-20 w-64 -translate-x-1/2 overflow-visible border border-slate-200 bg-white shadow-xl">
                    <div className="absolute -top-3 left-1/2 z-10 h-3 w-px -translate-x-1/2 bg-slate-300" />
                    {item.image && (
                      <div className="relative h-[74px] w-full overflow-hidden rounded-t-lg">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={item.image} alt="" className="h-full w-full object-cover" />
                        <div
                          className="absolute inset-0"
                          style={{ background: `linear-gradient(180deg, ${accent}38 0%, rgba(255,255,255,0) 46%, rgba(255,255,255,0.97) 100%)` }}
                        />
                      </div>
                    )}
                    <CardHeader className="pb-2 pt-3">
                      <div className="flex items-center justify-between">
                        <Badge className={`border px-2 text-[10px] font-bold uppercase tracking-wider ${getStatusStyles(item.status)}`}>
                          {item.status === "completed"
                            ? "STRONG"
                            : item.status === "in-progress"
                              ? "HARDEST"
                              : "PENDING"}
                        </Badge>
                        <span className="font-mono text-xs text-slate-400">{item.date}</span>
                      </div>
                      <CardTitle className="mt-2 text-sm" style={{ color: accent }}>
                        {item.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs leading-relaxed text-slate-600">
                      <p>{item.content}</p>

                      <div className="mt-4 border-t border-slate-100 pt-3">
                        <div className="mb-1 flex items-center justify-between text-xs text-slate-500">
                          <span className="flex items-center">
                            <Zap size={10} className="mr-1" />
                            Test F1
                          </span>
                          <span className="font-mono text-slate-700">{(item.energy / 100).toFixed(2)}</span>
                        </div>
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${item.energy}%`, background: accent }}
                          />
                        </div>
                      </div>

                      {item.relatedIds.length > 0 && (
                        <div className="mt-4 border-t border-slate-100 pt-3">
                          <div className="mb-2 flex items-center">
                            <Link size={10} className="mr-1 text-slate-400" />
                            <h4 className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
                              Confused with
                            </h4>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {item.relatedIds.map((relatedId) => {
                              const relatedItem = timelineData.find((i) => i.id === relatedId);
                              return (
                                <Button
                                  key={relatedId}
                                  variant="outline"
                                  size="sm"
                                  className="flex h-6 items-center rounded-full border border-slate-200 bg-white px-2.5 py-0 text-xs text-slate-600 transition-all hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleItem(relatedId);
                                  }}
                                >
                                  {relatedItem?.title}
                                  <ArrowRight size={8} className="ml-1 text-slate-400" />
                                </Button>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
