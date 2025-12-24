"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BarChart3,
  LayoutDashboard,
  Users,
  FileText,
  Database,
  Settings,
  LogOut,
  ChevronRight,
  Building2,
  X,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface NavItemProps {
  href: string;
  icon: React.ElementType;
  label: string;
  isCollapsed: boolean;
}

function NavItem({ href, icon: Icon, label, isCollapsed }: NavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

  const content = (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group",
        isActive
          ? "text-blue-600 bg-blue-500/10"
          : "text-slate-600 hover:text-slate-900 hover:bg-slate-100",
        isCollapsed && "justify-center px-2"
      )}
    >
      <Icon className="w-5 h-5 min-w-[20px]" />
      {!isCollapsed && (
        <>
          <span>{label}</span>
          <ChevronRight className="w-4 h-4 ml-auto opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0" />
        </>
      )}
    </Link>
  );

  if (isCollapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent side="right">
          <p>{label}</p>
        </TooltipContent>
      </Tooltip>
    );
  }

  return content;
}

export default function Sidebar() {
  const { user, isAdmin, simulatedClient, logout, simulateAsClient } =
    useAuth();
  const router = useRouter();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    // Small delay to ensure state updates before navigation
    setTimeout(() => {
      router.push("/login");
    }, 100);
  };

  const handleStopSimulation = () => {
    simulateAsClient(null);
    router.push("/admin/clients");
  };

  return (
    <aside
      className={cn(
        "h-screen flex flex-col bg-white border-r border-slate-200 transition-all duration-300 relative",
        isCollapsed ? "w-20" : "w-64"
      )}
    >
      <Button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-8 z-20 h-6 w-6 rounded-full border border-slate-200 bg-white p-0 shadow-sm hover:bg-slate-100"
        variant="ghost"
      >
        <PanelLeft className="h-3 w-3 text-slate-500" />
      </Button>

      {/* Logo */}
      <div className="p-6 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shrink-0">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          {!isCollapsed && (
            <div>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">
                Gold Standard
              </span>
              <p className="text-xs text-slate-500">Analytics Dashboard</p>
            </div>
          )}
        </div>
      </div>

      {/* Simulation Banner */}
      {simulatedClient && (
        <div
          className={cn(
            "mx-4 mt-4",
            isCollapsed
              ? "p-1"
              : "p-3 rounded-lg bg-blue-500/10 border border-blue-500/20"
          )}
        >
          {!isCollapsed ? (
            <>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-blue-600">
                  <Building2 className="w-4 h-4" />
                  <span className="font-medium">Viewing as:</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-500/20"
                  onClick={handleStopSimulation}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-sm font-semibold text-slate-900 mt-1">
                {simulatedClient.name}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="w-full mt-2 text-xs h-7 border-blue-500/30 text-blue-600 hover:bg-blue-500/20"
                onClick={handleStopSimulation}
              >
                Stop Viewing as Client
              </Button>
            </>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full h-8 text-blue-600 bg-blue-500/10"
                >
                  <Building2 className="w-4 h-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Viewing as: {simulatedClient.name}</p>
                <p className="text-xs text-slate-400">
                  Click to expand and stop
                </p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <div className="mb-4">
          {!isCollapsed && (
            <p className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Overview
            </p>
          )}
          <NavItem
            href="/dashboard"
            icon={LayoutDashboard}
            label={
              simulatedClient || user?.role === "client"
                ? "Performance"
                : "Dashboard"
            }
            isCollapsed={isCollapsed}
          />
          {(simulatedClient || user?.role === "client") && (
            <NavItem
              href="/reports"
              icon={FileText}
              label="Reports"
              isCollapsed={isCollapsed}
            />
          )}
        </div>

        {isAdmin && !simulatedClient && (
          <div className="mb-4">
            {!isCollapsed && (
              <p className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                Admin
              </p>
            )}
            <NavItem
              href="/admin/clients"
              icon={Users}
              label="Clients"
              isCollapsed={isCollapsed}
            />
            <NavItem
              href="/admin/ingestion"
              icon={Database}
              label="Data Ingestion"
              isCollapsed={isCollapsed}
            />
            <NavItem
              href="/admin/settings"
              icon={Settings}
              label="Settings"
              isCollapsed={isCollapsed}
            />
          </div>
        )}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-slate-200">
        <div
          className={cn(
            "flex items-center gap-3 rounded-lg bg-slate-100 mb-3",
            isCollapsed ? "p-2 justify-center" : "px-3 py-2"
          )}
        >
          <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
            <span className="text-sm font-semibold text-blue-600">
              {user?.email?.charAt(0).toUpperCase()}
            </span>
          </div>
          {!isCollapsed && (
            <>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {user?.email?.split("@")[0]}
                </p>
                <p className="text-xs text-slate-500 capitalize">
                  {user?.role}
                </p>
              </div>
            </>
          )}
        </div>

        <Button
          variant="ghost"
          size="sm"
          className={cn(
            "w-full text-slate-600 hover:text-slate-900",
            isCollapsed ? "justify-center px-0" : "justify-start"
          )}
          onClick={handleLogout}
        >
          <LogOut className={cn("w-4 h-4", !isCollapsed && "mr-2")} />
          {!isCollapsed && "Sign out"}
        </Button>
      </div>
    </aside>
  );
}
