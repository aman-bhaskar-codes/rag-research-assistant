"use client";
import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle2 } from "lucide-react";

interface CapabilityRecord {
  category: string;
  attempts: number;
  success_rate: number;
  avg_quality: number;
  avg_steps: number;
  is_weak: boolean;
  common_failure: string | null;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function CapabilityDashboard() {
  const [data, setData] = useState<CapabilityRecord[]>([]);
  const [weakAreas, setWeakAreas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/agent/capability-map`)
      .then(r => r.json())
      .then(d => {
        setData(d.capability_map || []);
        setWeakAreas(d.weak_areas || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse h-32 bg-plex-surface rounded-xl" />;
  if (!data.length) return (
    <div className="text-center py-8 text-plex-muted text-sm">
      No capability data yet. Run some agent tasks first.
    </div>
  );

  const getQualityColor = (q: number) =>
    q >= 0.7 ? "text-green-400" : q >= 0.5 ? "text-amber-400" : "text-red-400";

  const QualityIcon = ({ q }: { q: number }) =>
    q >= 0.7 ? <TrendingUp className="w-3.5 h-3.5 text-green-400" /> :
    q >= 0.5 ? <Minus className="w-3.5 h-3.5 text-amber-400" /> :
    <TrendingDown className="w-3.5 h-3.5 text-red-400" />;

  return (
    <div>
      <h3 className="text-sm font-semibold text-plex-text mb-4 flex items-center gap-2">
        Agent Capability Map
        {weakAreas.length > 0 && (
          <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">
            {weakAreas.length} weak area{weakAreas.length > 1 ? "s" : ""}
          </span>
        )}
      </h3>

      <div className="space-y-2">
        {data.map(rec => (
          <div
            key={rec.category}
            className={`p-3 rounded-xl border ${rec.is_weak
              ? "bg-red-500/5 border-red-500/20"
              : "bg-plex-surface border-plex-border"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                {rec.is_weak
                  ? <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  : <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
                }
                <span className="text-xs font-medium text-plex-text">
                  {rec.category.replace(/_/g, " ")}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <QualityIcon q={rec.avg_quality} />
                <span className={`text-xs font-bold ${getQualityColor(rec.avg_quality)}`}>
                  {(rec.avg_quality * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-1">
              <div className="w-full h-1.5 bg-plex-border rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${rec.is_weak ? "bg-red-500" : "bg-green-500"}`}
                  style={{ width: `${rec.avg_quality * 100}%` }}
                />
              </div>
              <span className="text-[10px] text-plex-muted whitespace-nowrap">
                {rec.attempts} runs · {rec.avg_steps.toFixed(1)} avg steps
              </span>
            </div>

            {rec.is_weak && rec.common_failure && (
              <p className="text-[10px] text-amber-400 mt-1">
                Common failure: {rec.common_failure.replace(/_/g, " ")}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
