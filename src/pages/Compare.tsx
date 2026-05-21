import { useState } from "react";
import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Company } from "@/types/company";
import { GitCompareArrows } from "lucide-react";

const ROWS: { label: string; key: keyof Company }[] = [
  { label: "Category", key: "category" },
  { label: "Employee size", key: "employee_size" },
  { label: "Hiring velocity", key: "hiring_velocity" },
  { label: "Profitability", key: "profitability_status" },
  { label: "Remote policy", key: "remote_policy_details" },
  { label: "YoY growth", key: "yoy_growth_rate" },
  { label: "Brand value", key: "brand_value" },
  { label: "Tech stack", key: "tech_stack" },
  { label: "AI/ML adoption", key: "ai_ml_adoption_level" },
  { label: "Automation level", key: "automation_level" },
];

export default function Compare() {
  const { data: companies = [] } = useCompanies();
  const [a, setA] = useState<string>("");
  const [b, setB] = useState<string>("");

  const ca = companies.find(c => String(c.company_id) === a);
  const cb = companies.find(c => String(c.company_id) === b);

  return (
    <div>
      <PageHeader
        eyebrow="Compare"
        title="Side-by-side Comparison"
        description="Pick two companies to evaluate strengths, trade-offs, and risks across 1:1 schema fields."
      />

      {companies.length === 0 ? (
        <EmptyState icon={<GitCompareArrows className="h-5 w-5" />} />
      ) : (
        <>
          <div className="grid sm:grid-cols-2 gap-3 mb-6">
            <CompanyPicker label="Company A" companies={companies} value={a} onChange={setA} />
            <CompanyPicker label="Company B" companies={companies} value={b} onChange={setB} />
          </div>

          {ca && cb ? (
            <div className="overflow-x-auto rounded-xl border border-border bg-surface">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-surface-muted">
                    <th className="text-left px-5 py-3 font-medium text-muted-foreground">Field</th>
                    <th className="text-left px-5 py-3 font-display font-semibold">{ca.name}</th>
                    <th className="text-left px-5 py-3 font-display font-semibold">{cb.name}</th>
                  </tr>
                </thead>
                <tbody>
                  {ROWS.map(r => (
                    <tr key={String(r.key)} className="border-t border-border">
                      <td className="px-5 py-3 text-muted-foreground">{r.label}</td>
                      <td className="px-5 py-3 text-foreground">{String(ca[r.key] ?? "—")}</td>
                      <td className="px-5 py-3 text-foreground">{String(cb[r.key] ?? "—")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="border border-dashed border-border rounded-xl p-10 text-center text-muted-foreground text-sm">
              Select two companies to begin comparison.
            </div>
          )}
        </>
      )}
    </div>
  );
}

function CompanyPicker({ label, companies, value, onChange }: { label: string; companies: Company[]; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-1.5">{label}</div>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="h-11 bg-surface"><SelectValue placeholder="Choose company…" /></SelectTrigger>
        <SelectContent>
          {companies.map(c => <SelectItem key={String(c.company_id)} value={String(c.company_id)}>{c.name}</SelectItem>)}
        </SelectContent>
      </Select>
    </div>
  );
}
