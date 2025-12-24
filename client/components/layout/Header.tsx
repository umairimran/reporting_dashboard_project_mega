"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, LogOut, Building2, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, simulatedClient, simulateAsClient, isAdmin } =
    useAuth();

  const handleLogout = () => {
    logout();
    setTimeout(() => {
      router.push("/login");
    }, 100);
  };

  const handleStopSimulation = () => {
    simulateAsClient(null);
    router.push("/admin/clients");
  };

  const isDashboard = pathname === "/dashboard";
  const isReports = pathname === "/reports";
  const isAdminPage = pathname.startsWith("/admin");

  // Show client navigation when: 1) Admin simulating as client OR 2) Actual client user
  const showClientNav =
    (simulatedClient && isAdmin) || (!isAdmin && user?.role === "client");

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center px-8 relative">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
          <span className="font-bold text-lg text-white"> G</span>
        </div>
        <span className="text-lg font-bold  bg-clip-text text-black">
          Gold Standard
        </span>
      </div>

      {/* Navigation - Centered */}
      <nav className="absolute left-1/2 -translate-x-1/2 flex items-center gap-2 z-10">
        {showClientNav ? (
          /* Client View Navigation */
          <>
            <Link
              href="/dashboard"
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                isDashboard
                  ? "text-blue-600 bg-blue-500/10"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              )}
            >
              Performance
            </Link>
            <Link
              href="/reports"
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                isReports
                  ? "text-blue-600 bg-blue-500/10"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              )}
            >
              Reports
            </Link>
          </>
        ) : (
          /* Admin Navigation */
          <>
            <Link
              href="/dashboard"
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                isDashboard
                  ? "text-blue-600 bg-blue-500/10"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              )}
            >
              Dashboard
            </Link>
            <Link
              href="/admin"
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                isAdminPage
                  ? "text-blue-600 bg-blue-500/10"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              )}
            >
              Admin
            </Link>
          </>
        )}
      </nav>

      {/* Right Side - Viewing Banner and User Section */}
      <div className="ml-auto flex items-center gap-4">
        {/* Viewing as Client Banner */}
        {simulatedClient && isAdmin && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <Building2 className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-blue-600">
                Viewing as: {simulatedClient.name}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-blue-500/30 text-blue-600 hover:bg-blue-500/20"
              onClick={handleStopSimulation}
            >
              <X className="w-4 h-4" />
              Stop Viewing
            </Button>
          </div>
        )}

        {/* User Section */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
              <span className="text-sm font-semibold text-blue-600">
                {user?.email?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="text-sm">
              <p className="font-medium text-slate-900">
                {user?.email?.split("@")[0]}
              </p>
              <p className="text-xs text-slate-500 capitalize">{user?.role}</p>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            className="text-slate-600 hover:text-slate-900"
            onClick={handleLogout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}
