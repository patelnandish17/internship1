import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { CompanyCard } from "@/components/companies/CompanyCard";
import { mapCategory } from "@/lib/utils";

const MAIN_CATEGORIES = [
  "All",
  "Tech Giants",
  "Product Based",
  "Service Based",
  "Startup or Small Scale Industries"
];

export default function Categories() {
  const { data: companies = [] } = useCompanies();
  const [params, setParams] = useSearchParams();
  const active = params.get("cat") ?? "All";

  const list = useMemo(
    () => active === "All" ? companies : companies.filter(c => mapCategory(c.category) === active),
    [companies, active]
  );

  return (
    <div>
      <PageHeader
        eyebrow="Categories"
        title="Companies by Category"
        description="Explore companies grouped by their primary category from public.company.category."
      />

      <div className="flex flex-wrap gap-2 mb-6">
        {MAIN_CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setParams(cat === "All" ? {} : { cat })}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all ${
              active === cat
                ? "bg-gradient-brand text-brand-foreground border-transparent shadow-glow"
                : "bg-surface text-muted-foreground border-border hover:text-foreground"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {list.length === 0 ? (
        <EmptyState title={`No companies in "${active}"`} />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {list.map(c => <CompanyCard key={String(c.company_id)} company={c} />)}
        </div>
      )}
    </div>
  );
}
