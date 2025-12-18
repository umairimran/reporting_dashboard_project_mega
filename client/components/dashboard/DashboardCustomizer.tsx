"use client";

import { useState, useEffect } from "react";
import { Settings, ChevronUp, ChevronDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";

export interface KPIConfig {
  id: string;
  label: string;
  enabled: boolean;
  order: number;
}

export interface SectionConfig {
  id: string;
  label: string;
  order: number;
}

interface DashboardCustomizerProps {
  kpis: KPIConfig[];
  sections: SectionConfig[];
  onKPIsChange: (kpis: KPIConfig[]) => void;
  onSectionsChange: (sections: SectionConfig[]) => void;
}

export default function DashboardCustomizer({
  kpis,
  sections,
  onKPIsChange,
  onSectionsChange,
}: DashboardCustomizerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [localKPIs, setLocalKPIs] = useState(kpis);
  const [localSections, setLocalSections] = useState(sections);
  const [hoveredKPI, setHoveredKPI] = useState<string | null>(null);
  const [hoveredSection, setHoveredSection] = useState<string | null>(null);

  useEffect(() => {
    setLocalKPIs(kpis);
  }, [kpis]);

  useEffect(() => {
    setLocalSections(sections);
  }, [sections]);

  const handleKPIToggle = (id: string) => {
    const updated = localKPIs.map((kpi) =>
      kpi.id === id ? { ...kpi, enabled: !kpi.enabled } : kpi
    );
    setLocalKPIs(updated);
  };

  const moveKPI = (id: string, direction: "up" | "down") => {
    const currentIndex = localKPIs.findIndex((kpi) => kpi.id === id);
    if (currentIndex === -1) return;

    const newIndex = direction === "up" ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= localKPIs.length) return;

    const updated = [...localKPIs];
    [updated[currentIndex], updated[newIndex]] = [
      updated[newIndex],
      updated[currentIndex],
    ];

    // Update order values
    const reordered = updated.map((kpi, index) => ({ ...kpi, order: index }));
    setLocalKPIs(reordered);
  };

  const moveSection = (id: string, direction: "up" | "down") => {
    const currentIndex = localSections.findIndex(
      (section) => section.id === id
    );
    if (currentIndex === -1) return;

    const newIndex = direction === "up" ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= localSections.length) return;

    const updated = [...localSections];
    [updated[currentIndex], updated[newIndex]] = [
      updated[newIndex],
      updated[currentIndex],
    ];

    // Update order values
    const reordered = updated.map((section, index) => ({
      ...section,
      order: index,
    }));
    setLocalSections(reordered);
  };

  const handleSave = () => {
    onKPIsChange(localKPIs);
    onSectionsChange(localSections);
    setIsOpen(false);
  };

  const handleCancel = () => {
    setLocalKPIs(kpis);
    setLocalSections(sections);
    setIsOpen(false);
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        className="gap-2"
        onClick={() => setIsOpen(true)}
      >
        <Settings className="w-4 h-4" />
        Customize
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="bg-white max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Customize Dashboard</DialogTitle>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* KPIs Section */}
            <div>
              <h3 className="text-sm font-semibold text-slate-900 mb-3">
                KPI Metrics
              </h3>
              <p className="text-xs text-slate-600 mb-4">
                Select which KPIs to display and reorder them
              </p>
              <div className="space-y-2">
                {localKPIs.map((kpi, index) => (
                  <div
                    key={kpi.id}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-lg border border-slate-200 transition-all duration-200",
                      hoveredKPI === kpi.id && "bg-slate-50"
                    )}
                    onMouseEnter={() => setHoveredKPI(kpi.id)}
                    onMouseLeave={() => setHoveredKPI(null)}
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <Switch
                        checked={kpi.enabled}
                        onCheckedChange={() => handleKPIToggle(kpi.id)}
                      />
                      <span
                        className={cn(
                          "text-sm font-medium",
                          kpi.enabled ? "text-slate-900" : "text-slate-400"
                        )}
                      >
                        {kpi.label}
                      </span>
                    </div>

                    <div
                      className={cn(
                        "flex items-center gap-1 transition-opacity duration-200",
                        hoveredKPI === kpi.id ? "opacity-100" : "opacity-0"
                      )}
                    >
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => moveKPI(kpi.id, "up")}
                        disabled={index === 0}
                      >
                        <ChevronUp className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => moveKPI(kpi.id, "down")}
                        disabled={index === localKPIs.length - 1}
                      >
                        <ChevronDown className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Sections */}
            <div>
              <h3 className="text-sm font-semibold text-slate-900 mb-3">
                Dashboard Sections
              </h3>
              <p className="text-xs text-slate-600 mb-4">
                Reorder the dashboard sections (all sections are required)
              </p>
              <div className="space-y-2">
                {localSections.map((section, index) => (
                  <div
                    key={section.id}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-lg border border-slate-200 transition-all duration-200",
                      hoveredSection === section.id && "bg-slate-50"
                    )}
                    onMouseEnter={() => setHoveredSection(section.id)}
                    onMouseLeave={() => setHoveredSection(null)}
                  >
                    <span className="text-sm font-medium text-slate-900">
                      {section.label}
                    </span>

                    <div
                      className={cn(
                        "flex items-center gap-1 transition-opacity duration-200",
                        hoveredSection === section.id
                          ? "opacity-100"
                          : "opacity-0"
                      )}
                    >
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => moveSection(section.id, "up")}
                        disabled={index === 0}
                      >
                        <ChevronUp className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => moveSection(section.id, "down")}
                        disabled={index === localSections.length - 1}
                      >
                        <ChevronDown className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
              <Button variant="outline" onClick={handleCancel}>
                Cancel
              </Button>
              <Button onClick={handleSave}>Save Changes</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
