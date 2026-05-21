import { useState, useEffect, useRef } from "react";
import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import { cn } from "@/lib/utils";

export function UserProfile() {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Attempt to fetch real session
    supabase.auth.getSession().then(({ data }) => {
      if (data?.session?.user) {
        setUser({
          name: data.session.user.user_metadata?.full_name || "Admin User",
          email: data.session.user.email || "",
        });
      } else {
        // Mock fallback if not actually authenticated yet
        setUser({
          name: "Placement Admin",
          email: "admin@pesce.ac.in",
        });
      }
    });

    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user) {
        setUser({
          name: session.user.user_metadata?.full_name || "Admin User",
          email: session.user.email || "",
        });
      }
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  // Click outside to close
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleLogout() {
    await supabase.auth.signOut();
    navigate("/login");
  }

  const initials = user?.name?.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2) || "U";

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-center h-9 w-9 rounded-full bg-brand-soft border border-brand/20 shadow-sm hover:shadow-md transition-all hover:border-brand/40 group focus:outline-none focus:ring-2 focus:ring-brand/40 focus:ring-offset-2 focus:ring-offset-surface"
      >
        <span className="font-display font-bold text-sm text-brand group-hover:scale-105 transition-transform">
          {initials}
        </span>
      </button>

      <div
        className={cn(
          "absolute right-0 mt-2 w-64 rounded-2xl bg-surface border border-border shadow-elevated overflow-hidden transition-all duration-200 origin-top-right z-50",
          open ? "opacity-100 scale-100 translate-y-0" : "opacity-0 scale-95 -translate-y-2 pointer-events-none"
        )}
      >
        <div className="p-4 bg-surface-muted/50">
          <div className="font-display font-bold text-foreground text-base truncate">
            {user?.name}
          </div>
          <div className="text-xs text-muted-foreground truncate mt-0.5">
            {user?.email}
          </div>
        </div>

        <div className="h-px bg-border w-full" />

        <div className="p-2">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-destructive hover:bg-destructive/10 hover:text-destructive transition-colors focus:outline-none focus:ring-2 focus:ring-destructive/40"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
