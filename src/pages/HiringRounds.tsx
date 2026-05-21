import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { ListChecks } from "lucide-react";

const ROUNDS = ["Aptitude", "Coding", "Technical Interview", "HR Interview"];

export default function HiringRounds() {
  const { data: companies = [] } = useCompanies();

  return (
    <div>
      <PageHeader
        eyebrow="Hiring Rounds"
        title="Recruitment Process Library"
        description="Understand each company's typical hiring process and how to prepare."
      />

      {companies.length === 0 ? (
        <EmptyState icon={<ListChecks className="h-5 w-5" />} />
      ) : (
        <div className="space-y-3">
          {companies.map(c => (
            <div key={String(c.company_id)} className="rounded-xl border border-border bg-surface p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="font-display font-semibold">{c.name}</div>
                  <div className="text-xs text-muted-foreground">{c.category}</div>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-warning/10 text-warning font-medium">Difficulty: TBD</span>
              </div>
              <div className="grid sm:grid-cols-4 gap-2">
                {ROUNDS.map((r, i) => (
                  <div key={r} className="rounded-lg border border-border p-3 bg-surface-muted">
                    <div className="text-[10px] font-mono text-brand uppercase tracking-wider">Round {i + 1}</div>
                    <div className="text-sm font-medium mt-1">{r}</div>
                    <div className="text-[11px] text-muted-foreground mt-2">Preparation tips appear here.</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
