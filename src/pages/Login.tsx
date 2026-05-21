import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, GraduationCap, Building2, Loader2, Sparkles, ShieldCheck, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { supabase } from "@/lib/supabase";

type Mode = "student" | "college";

export default function Login() {
  const [mode, setMode] = useState<Mode>("student");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!identifier.trim() || !password) {
      setError("Please fill in all fields.");
      return;
    }
    setLoading(true);
    try {
      const { data, error: err } = await supabase.auth.signInWithPassword({
        email: identifier,
        password: password,
      });
      if (err) {
        setError(err.message);
      } else {
        navigate(mode === "student" ? "/home" : "/analytics");
      }
    } catch (err: any) {
      setError(err?.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-surface">
      {/* LEFT — branding */}
      <div className="hidden lg:flex relative overflow-hidden p-12 flex-col justify-between text-white">
        {/* Background Image with Zoom Effect */}
        <div 
          className="absolute inset-0 bg-cover bg-center transition-transform duration-700 hover:scale-105" 
          style={{ backgroundImage: 'url("/pes-campus.png")' }}
        />
        {/* Sleek Dark Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/70 to-slate-950/80" />

        <div className="flex items-center gap-3 relative z-10 bg-black/30 backdrop-blur-md px-4 py-2.5 rounded-xl border border-white/10 self-start shadow-md">
          <img 
            src="/pes-logo.png" 
            alt="PESCE Logo" 
            className="h-10 w-auto bg-white/90 p-1.5 rounded-md"
          />
          <div>
            <div className="font-display font-semibold text-white tracking-wide">PESCE Mandya</div>
            <div className="text-[10px] text-white/70 tracking-wider uppercase font-semibold">Placement Intelligence</div>
          </div>
        </div>

        <div className="relative z-10 max-w-md bg-black/40 backdrop-blur-md p-7 rounded-2xl border border-white/10 shadow-lg">
          <h1 className="font-display text-4xl font-bold text-white text-balance leading-tight">
            Decision-grade analytics for <span className="text-brand-foreground bg-brand px-2 py-0.5 rounded-md inline-block mt-1 font-semibold shadow-glow">campus hiring</span>.
          </h1>
          <p className="mt-4 text-white/80 text-sm leading-relaxed">
            Explore companies, compare opportunities, and map your skills against real hiring signals.
          </p>

          <div className="mt-6 grid gap-3">
            {[
              { icon: BarChart3, t: "163 data points per company" },
              { icon: Sparkles, t: "Skill-to-role fit mapping" },
              { icon: ShieldCheck, t: "Verified institutional data" },
            ].map(({ icon: I, t }) => (
              <div key={t} className="flex items-center gap-3 text-xs">
                <div className="h-8 w-8 rounded-lg bg-white/10 backdrop-blur-sm grid place-items-center text-brand">
                  <I className="h-4 w-4 text-brand-foreground" />
                </div>
                <span className="text-white/90 font-medium">{t}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 text-[10px] text-white/60 font-medium">
          © {new Date().getFullYear()} PESCE Mandya · Placement Intelligence
        </div>
      </div>

      {/* RIGHT — form */}
      <div className="flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md">
          <div className="flex flex-col items-center text-center mb-8">
            <img 
              src="/pes-logo.png" 
              alt="PES College of Engineering" 
              className="h-28 w-auto mb-5 drop-shadow-md"
            />
            <h1 className="text-xl sm:text-2xl font-display font-bold text-foreground tracking-tight">
              P.E.S College of Engineering, Mandya 571401
            </h1>
            <p className="text-sm font-medium text-muted-foreground mt-2">
              (An Autonomous Institute affiliated to VTU, Belagavi)
            </p>
          </div>

          <div className="text-center">
            <h2 className="font-display text-2xl font-bold">Welcome back</h2>
            <p className="text-sm text-muted-foreground mt-1">Sign in to continue to your dashboard.</p>
          </div>

          {/* tabs */}
          <div className="mt-6 grid grid-cols-2 p-1 rounded-lg bg-surface-muted">
            {(["student", "college"] as Mode[]).map(m => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(null); }}
                className={cn(
                  "relative flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all",
                  mode === m ? "bg-surface text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
                )}
              >
                {m === "student" ? <GraduationCap className="h-4 w-4" /> : <Building2 className="h-4 w-4" />}
                {m === "student" ? "Student" : "College"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="id">{mode === "student" ? "Email address" : "Official email or Admin ID"}</Label>
              <Input
                id="id"
                type={mode === "student" ? "email" : "text"}
                placeholder={mode === "student" ? "you@pesce.ac.in" : "admin@pesce.ac.in"}
                value={identifier}
                onChange={e => setIdentifier(e.target.value)}
                className="h-11 bg-surface focus-visible:ring-brand/40 focus-visible:border-brand transition-all"
                autoComplete="username"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="pwd">Password</Label>
                <button type="button" className="text-xs text-brand hover:underline">Forgot password?</button>
              </div>
              <div className="relative">
                <Input
                  id="pwd"
                  type={showPwd ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="h-11 pr-10 bg-surface focus-visible:ring-brand/40 focus-visible:border-brand"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  aria-label="Toggle password visibility"
                >
                  {showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="text-xs px-3 py-2 rounded-md bg-destructive/10 text-destructive border border-destructive/20">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-11 bg-gradient-brand hover:opacity-95 text-brand-foreground font-medium shadow-glow"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : `Sign in as ${mode === "student" ? "Student" : "College"}`}
            </Button>

            {mode === "student" && (
              <>
                <div className="relative py-1">
                  <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-border" /></div>
                  <div className="relative flex justify-center text-[11px] uppercase tracking-wider">
                    <span className="bg-surface px-2 text-muted-foreground">or continue with</span>
                  </div>
                </div>
                <Button type="button" variant="outline" className="w-full h-11">
                  <svg className="h-4 w-4 mr-2" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.83z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.83C6.71 7.31 9.14 5.38 12 5.38z"/></svg>
                  Continue with Google
                </Button>
              </>
            )}
          </form>

          <p className="mt-8 text-center text-xs text-muted-foreground">
            Protected by institutional access policy.
          </p>
        </div>
      </div>
    </div>
  );
}
