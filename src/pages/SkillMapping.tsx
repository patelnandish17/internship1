import { useMemo, useState } from "react";
import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { Company } from "@/types/company";
import { Brain, X } from "lucide-react";

function asArray(v: unknown): string[] {
  if (Array.isArray(v)) return v.map(String);
  if (typeof v === "string" && v.length) return v.split(",").map(s => s.trim());
  return [];
}

function computeFit(company: Company, skills: string[]): { score: number; matched: string[]; gaps: string[] } {
  const required = [
    ...asArray(company.tech_stack),
    ...asArray(company.skill_relevance),
  ].map(s => s.toLowerCase());
  const userSet = new Set(skills.map(s => s.toLowerCase()));
  const matched = required.filter(r => userSet.has(r));
  const gaps = required.filter(r => !userSet.has(r));
  const score = required.length === 0 ? 0 : matched.length / required.length;
  return { score, matched, gaps };
}

export default function SkillMapping() {
  const { data: companies = [] } = useCompanies();
  const [input, setInput] = useState("");
  const [skills, setSkills] = useState<string[]>([]);

  function add() {
    const v = input.trim();
    if (!v || skills.includes(v)) return;
    setSkills([...skills, v]);
    setInput("");
  }

  const matches = useMemo(
    () => companies.map(c => ({ company: c, ...computeFit(c, skills) }))
      .sort((x, y) => y.score - x.score),
    [companies, skills]
  );

  return (
    <div>
      <PageHeader
        eyebrow="Skill Mapping"
        title="Rule-based Fit Engine"
        description="Match your skills against tech_stack, ai_ml_adoption_level, automation_level, and skill_relevance."
      />

      <div className="rounded-xl border border-border bg-surface p-5 mb-6">
        <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Add your skills</div>
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && (e.preventDefault(), add())}
            placeholder="e.g. React, Python, SQL…"
            className="h-11 bg-surface"
          />
          <Button onClick={add} className="h-11 bg-brand text-brand-foreground hover:bg-brand/90">Add</Button>
        </div>
        <div className="flex flex-wrap gap-2 mt-3 min-h-[28px]">
          {skills.map(s => (
            <span key={s} className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-brand-soft text-brand">
              {s}
              <button onClick={() => setSkills(skills.filter(x => x !== s))}><X className="h-3 w-3" /></button>
            </span>
          ))}
        </div>
      </div>

      {companies.length === 0 ? (
        <EmptyState icon={<Brain className="h-5 w-5" />} />
      ) : skills.length === 0 ? (
        <div className="border border-dashed border-border rounded-xl p-10 text-center text-sm text-muted-foreground">
          Add at least one skill to see fit results.
        </div>
      ) : (
        <div className="grid gap-3">
          {matches.map(({ company, score, gaps }) => {
            const tier = score >= 0.66 ? "High" : score >= 0.33 ? "Medium" : "Low";
            const tierColor = tier === "High" ? "text-success bg-success/10" : tier === "Medium" ? "text-warning bg-warning/10" : "text-muted-foreground bg-muted";
            return (
              <div key={String(company.company_id)} className="rounded-xl border border-border bg-surface p-5 flex flex-col sm:flex-row gap-4">
                <div className="flex-1 min-w-0">
                  <div className="font-display font-semibold">{company.name}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">{company.category}</div>
                  {gaps.length > 0 && (
                    <div className="mt-3 text-xs">
                      <span className="text-muted-foreground">Skill gaps:</span>{" "}
                      <span className="text-foreground">{gaps.slice(0, 6).join(", ")}</span>
                    </div>
                  )}
                </div>
                <div className="flex sm:flex-col items-end gap-3 sm:gap-2">
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${tierColor}`}>{tier} fit</span>
                  <div className="font-display font-bold text-2xl text-foreground">{Math.round(score * 100)}%</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
