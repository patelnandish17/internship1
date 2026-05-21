import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  LayoutGrid,
  GitCompareArrows,
  Brain,
  BarChart3,
  ListChecks,
  Sparkles,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { UserProfile } from "./UserProfile";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/home", label: "Home", icon: LayoutDashboard },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/categories", label: "Categories", icon: LayoutGrid },
  { to: "/compare", label: "Compare", icon: GitCompareArrows },
  { to: "/skill-mapping", label: "Skill Mapping", icon: Brain },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/hiring-rounds", label: "Hiring Rounds", icon: ListChecks },
  { to: "/innovox", label: "Innovox", icon: Sparkles },
];

export default function AppLayout() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-surface-muted">
      {/* Topbar (mobile) */}
      <header className="lg:hidden sticky top-0 z-40 flex items-center justify-between border-b border-border bg-surface px-4 h-14">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-brand grid place-items-center text-brand-foreground font-display font-bold text-sm">P</div>
          <span className="font-display font-semibold text-sm">PESCE PI</span>
        </div>
        <div className="flex items-center gap-3">
          <UserProfile />
          <button onClick={() => setOpen(v => !v)} className="p-2 rounded-md hover:bg-surface-muted">
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={cn(
          "fixed lg:sticky top-0 left-0 z-30 h-screen w-64 shrink-0 border-r border-border bg-surface flex-col transition-transform",
          "lg:flex lg:translate-x-0",
          open ? "flex translate-x-0" : "flex -translate-x-full lg:translate-x-0"
        )}>
          <div className="hidden lg:flex items-center gap-3 px-5 h-16 border-b border-border">
            <div className="h-9 w-9 rounded-lg bg-gradient-brand grid place-items-center text-brand-foreground font-display font-bold">P</div>
            <div className="leading-tight">
              <div className="font-display font-semibold text-sm">PESCE Mandya</div>
              <div className="text-[11px] text-muted-foreground tracking-wide uppercase">Placement Intelligence</div>
            </div>
          </div>

          <nav className="flex-1 overflow-y-auto p-3 space-y-0.5 scrollbar-thin">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-brand-soft text-brand"
                      : "text-muted-foreground hover:bg-surface-muted hover:text-foreground"
                  )
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0 lg:ml-0 flex flex-col h-screen overflow-hidden">
          {/* Top Header (Desktop) */}
          <header className="hidden lg:flex h-16 shrink-0 items-center justify-end px-8 border-b border-border bg-surface/50 backdrop-blur-sm sticky top-0 z-20">
            <UserProfile />
          </header>

          <div className="flex-1 overflow-y-auto">
            <div className="max-w-[1400px] mx-auto p-4 sm:p-6 lg:p-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
