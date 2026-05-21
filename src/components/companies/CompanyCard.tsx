import { useState } from "react";
import type { Company } from "@/types/company";
import { Badge } from "@/components/ui/badge";
import { Building2, TrendingUp, Users } from "lucide-react";
import { Link } from "react-router-dom";

function asArray(v: unknown): string[] {
  if (Array.isArray(v)) return v as string[];
  if (typeof v === "string" && v.length) return v.split(",").map(s => s.trim());
  return [];
}

function extractLogoUrl(raw: string | null | undefined): string | null {
  if (!raw || raw === "null") return null;
  const firstPart = raw.split(';')[0].trim();
  const urlOnly = firstPart.split(' ')[0].trim();
  if (!urlOnly.startsWith('http')) return null;
  return urlOnly;
}

export function CompanyCard({ company }: { company: Company }) {
  const [imgError, setImgError] = useState(false);
  const sectors = asArray(company.focus_sectors).slice(0, 3);
  const logoSrc = extractLogoUrl(company.logo_url);
  
  return (
    <Link
      to={`/company/${company.company_id}`}
      className="group block rounded-xl border border-border bg-surface p-5 hover:shadow-elevated hover:border-brand/30 transition-all"
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="h-11 w-11 rounded-lg bg-brand-soft grid place-items-center overflow-hidden shrink-0">
          {logoSrc && !imgError ? (
            <img src={logoSrc} alt={company.name || "Company Logo"} className="h-full w-full object-cover" onError={() => setImgError(true)} />
          ) : (
            <Building2 className="h-5 w-5 text-brand" />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-display font-semibold text-foreground truncate group-hover:text-brand transition-colors">
            {company.name}
          </h3>
          {company.short_name && (
            <div className="text-xs text-muted-foreground font-mono">{company.short_name}</div>
          )}
        </div>
        {company.category && (
          <Badge variant="secondary" className="bg-brand-soft text-brand border-0 text-[10px] shrink truncate max-w-[120px]">
            {company.category}
          </Badge>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5 mb-4 min-h-[24px]">
        {sectors.map(s => (
          <span key={s} className="text-[11px] px-2 py-0.5 rounded-full bg-surface-muted text-muted-foreground truncate max-w-full inline-block" title={s}>
            {s}
          </span>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-border text-xs">
        <Stat icon={<Users className="h-3 w-3" />} label="Size" value={company.employee_size ?? "—"} />
        <Stat icon={<TrendingUp className="h-3 w-3" />} label="Hiring" value={company.hiring_velocity ?? "—"} />
        <Stat label="Profit" value={company.profitability_status ?? "—"} />
      </div>
    </Link>
  );
}

function Stat({ icon, label, value }: { icon?: React.ReactNode; label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-1 text-muted-foreground text-[10px] uppercase tracking-wide">
        {icon}{label}
      </div>
      <div className="font-medium text-foreground truncate text-xs mt-0.5">{String(value)}</div>
    </div>
  );
}
