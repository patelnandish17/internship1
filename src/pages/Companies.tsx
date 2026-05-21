import { useMemo, useState } from "react";
import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { CompanyCard } from "@/components/companies/CompanyCard";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function Companies() {
  const { data: companies = [], isLoading } = useCompanies();
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("name");

  const filtered = useMemo(() => {
    const list = companies.filter(c =>
      !q || String(c.name).toLowerCase().includes(q.toLowerCase())
    );
    return [...list].sort((a, b) => {
      if (sort === "name") return String(a.name).localeCompare(String(b.name));
      if (sort === "employee_size") return Number(b.employee_size ?? 0) - Number(a.employee_size ?? 0);
      if (sort === "yoy_growth_rate") return Number(b.yoy_growth_rate ?? 0) - Number(a.yoy_growth_rate ?? 0);
      if (sort === "brand_value") return Number(b.brand_value ?? 0) - Number(a.brand_value ?? 0);
      return 0;
    });
  }, [companies, q, sort]);

  return (
    <div>
      <PageHeader
        eyebrow="Directory"
        title="All Companies"
        description="Filter, sort, and explore every recruiting partner."
      />

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <Input
          placeholder="Search companies…"
          value={q}
          onChange={e => setQ(e.target.value)}
          className="h-11 bg-surface flex-1"
        />
        <Select value={sort} onValueChange={setSort}>
          <SelectTrigger className="h-11 sm:w-56 bg-surface"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Sort by Name</SelectItem>
            <SelectItem value="employee_size">Sort by Employee Size</SelectItem>
            <SelectItem value="yoy_growth_rate">Sort by YoY Growth</SelectItem>
            <SelectItem value="brand_value">Sort by Brand Value</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="h-44 rounded-xl bg-surface border border-border animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(c => <CompanyCard key={String(c.company_id)} company={c} />)}
        </div>
      )}
    </div>
  );
}
