import { useMemo, useState } from "react";
import { Search, Building2, Layers, TrendingUp, Briefcase } from "lucide-react";
import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { CompanyCard } from "@/components/companies/CompanyCard";
import { Input } from "@/components/ui/input";
import { Link } from "react-router-dom";
import { mapCategory } from "@/lib/utils";

const CATEGORY_TILES = [
  { key: "Tech Giants", icon: Layers, hint: "Large cap & multinational orgs" },
  { key: "Product Based", icon: Briefcase, hint: "Product & SaaS companies" },
  { key: "Service Based", icon: Building2, hint: "IT services & consulting" },
  { key: "Startup or Small Scale Industries", icon: TrendingUp, hint: "High-growth startups & SMBs" },
];

export default function Home() {
  const { data: companies = [], isLoading } = useCompanies();
  const [q, setQ] = useState("");

  const counts = useMemo(() => {
    const map: Record<string, number> = {};
    companies.forEach(c => {
      const k = mapCategory(c.category);
      map[k] = (map[k] ?? 0) + 1;
    });
    return map;
  }, [companies]);

  return (
    <div>
      <PageHeader
        eyebrow="Overview"
        title="Placement Intelligence Dashboard"
        description="A unified view of every company recruiting at PESCE Mandya — backed by 163 verified data points."
      />

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        <StatCard label="Total companies" value={companies.length} accent="brand" />
        <StatCard label="Categories" value={Object.keys(counts).length} accent="violet" />
        <StatCard label="Hiring active" value={companies.filter(c => c.hiring_velocity === "High").length} accent="teal" />
        <StatCard label="Profitable" value={companies.filter(c => String(c.profitability_status).toLowerCase().includes("profit")).length} accent="amber" />
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by name, tech_stack, or focus_sectors…"
          value={q}
          onChange={e => setQ(e.target.value)}
          className="h-12 pl-11 bg-surface border-border focus-visible:ring-brand/40"
        />
      </div>

      {/* Category tiles */}
      <h2 className="font-display font-semibold text-lg mb-3">Browse by category</h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-10">
        {CATEGORY_TILES.map(({ key, icon: Icon, hint }) => (
          <Link
            key={key}
            to={`/categories?cat=${key}`}
            className="group rounded-xl border border-border bg-surface p-5 hover:border-brand/40 hover:shadow-elevated transition-all"
          >
            <div className="h-10 w-10 rounded-lg bg-brand-soft text-brand grid place-items-center mb-3 group-hover:bg-gradient-brand group-hover:text-brand-foreground transition-all">
              <Icon className="h-5 w-5" />
            </div>
            <div className="font-display font-semibold">{key}</div>
            <div className="text-xs text-muted-foreground mt-0.5">{hint}</div>
            <div className="text-2xl font-display font-bold text-brand mt-3">{counts[key] ?? 0}</div>
          </Link>
        ))}
      </div>

      {/* Insights */}
      <h2 className="font-display font-semibold text-lg mb-3">Latest companies</h2>
      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-44 rounded-xl bg-surface border border-border animate-pulse" />
          ))}
        </div>
      ) : companies.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.slice(0, 6).map(c => <CompanyCard key={String(c.company_id)} company={c} />)}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, accent }: { label: string; value: number; accent: "brand" | "violet" | "teal" | "amber" }) {
  const map = {
    brand: "from-brand/10 to-brand/0 text-brand",
    violet: "from-accent-violet/10 to-transparent text-accent-violet",
    teal: "from-accent-teal/10 to-transparent text-accent-teal",
    amber: "from-accent-amber/10 to-transparent text-accent-amber",
  } as const;
  return (
    <div className={`rounded-xl border border-border bg-gradient-to-br ${map[accent]} bg-surface p-5`}>
      <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="font-display text-3xl font-bold text-foreground mt-1.5">{value}</div>
    </div>
  );
}
