"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    setTimeout(() => {
      router.push("/login");
    }, 100);
  };

  const isDashboard = pathname === "/dashboard";
  const isAdmin = pathname.startsWith("/admin");

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
          <BarChart3 className="w-6 h-6 text-white" />
        </div>
        <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">
          Gold Standard
        </span>
      </div>

      {/* Navigation - Centered */}
      <nav className="absolute left-1/2 -translate-x-1/2 flex items-center gap-2">
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
            isAdmin
              ? "text-blue-600 bg-blue-500/10"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          )}
        >
          Admin
        </Link>
      </nav>

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
    </header>
  );
}
