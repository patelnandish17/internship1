import { PageHeader } from "@/components/common/PageHeader";
import { useCompanies } from "@/hooks/useCompanies";
import { Sparkles, Cpu, TrendingUp, Lightbulb, ArrowUpRight } from "lucide-react";

const PANELS = [
  { icon: Cpu, title: "Emerging Tech Trends", body: "Aggregated tech_stack and ai_ml_adoption_level signals across recruiting partners." },
  { icon: TrendingUp, title: "High-growth Companies", body: "Ranked by yoy_growth_rate and hiring_velocity from public.company." },
  { icon: Lightbulb, title: "Skill Demand Insights", body: "Most-requested skills derived from skill_relevance frequency." },
];

export default function Innovox() {
  const { data: companies = [] } = useCompanies();

  return (
    <div>
      <PageHeader
        eyebrow="Innovox"
        title="Innovation & Insights Layer"
        description="An extensible analytics surface for forward-looking placement intelligence."
        actions={
          <div className="hidden sm:flex items-center gap-2 text-xs text-brand bg-brand-soft px-3 py-1.5 rounded-full">
            <Sparkles className="h-3.5 w-3.5" /> Beta module
          </div>
        }
      />

      <div className="rounded-2xl bg-gradient-mesh border border-border p-6 sm:p-10 mb-6">
        <div className="max-w-2xl">
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-balance">
            Turn 163 columns of company data into <span className="text-brand">strategic foresight</span>.
          </h2>
          <p className="text-sm text-muted-foreground mt-3">
            Innovox surfaces patterns across hiring, tech adoption, and growth signals — designed to plug into the same Supabase schema.
          </p>
          <div className="mt-5 flex items-center gap-4 text-xs text-muted-foreground">
            <span><span className="font-display text-2xl font-bold text-foreground">{companies.length}</span> companies analyzed</span>
            <span className="h-4 w-px bg-border" />
            <span><span className="font-display text-2xl font-bold text-foreground">163</span> data points each</span>
          </div>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {PANELS.map(({ icon: Icon, title, body }) => (
          <div key={title} className="group rounded-xl border border-border bg-surface p-5 hover:shadow-elevated transition-all">
            <div className="flex items-start justify-between mb-3">
              <div className="h-10 w-10 rounded-lg bg-brand-soft text-brand grid place-items-center group-hover:bg-gradient-brand group-hover:text-brand-foreground transition-all">
                <Icon className="h-5 w-5" />
              </div>
              <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-brand transition-colors" />
            </div>
            <div className="font-display font-semibold">{title}</div>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">{body}</p>
            <div className="mt-4 h-24 rounded-md border border-dashed border-border grid place-items-center text-xs text-muted-foreground">
              Awaiting data
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
