import { useParams, Link } from "react-router-dom";
import { useCompany } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft } from "lucide-react";
import type { Company } from "@/types/company";

const TAB_MAPPINGS: Record<string, (keyof Company)[]> = {
  Overview: [
    "overview_text", "nature_of_company", "core_value_proposition", "vision_statement",
    "mission_statement", "core_values", "unique_differentiators", "competitive_advantages",
    "weaknesses_gaps", "key_challenges_needs", "key_competitors", "history_timeline",
    "recent_news", "awards_recognitions", "brand_sentiment_score", "event_participation",
    "regulatory_status", "legal_issues", "case_studies", "go_to_market_strategy",
    "marketing_video_url", "customer_testimonials", "network_strength", "external_recognition",
    "mission_clarity", "crisis_behavior", "ceo_name", "ceo_linkedin_url", "key_leaders",
    "board_members", "warm_intro_pathways", "decision_maker_access", "primary_contact_email",
    "primary_phone_number", "contact_person_name", "contact_person_title", "contact_person_email",
    "contact_person_phone", "technology_partners", "partnership_ecosystem", "industry_associations",
    "brand_value", "client_quality", "global_exposure", "incorporation_year", "employee_size",
    "focus_sectors", "offerings_description", "top_customers", "pain_points_addressed", "company_maturity", "exit_strategy_history"
  ],
  Hiring: [
    "hiring_velocity", "employee_turnover", "avg_retention_tenure", "onboarding_quality",
    "learning_culture", "internal_mobility", "promotion_clarity", "role_clarity",
    "early_ownership", "work_impact", "execution_thinking_balance", "skill_relevance",
    "exposure_quality", "mentorship_availability", "exit_opportunities", "cross_functional_exposure"
  ],
  Tech: [
    "tech_stack", "ai_ml_adoption_level", "automation_level", "cybersecurity_posture",
    "tools_access", "tech_adoption_rating"
  ],
  Culture: [
    "work_culture_summary", "manager_quality", "psychological_safety", "feedback_culture",
    "diversity_inclusion_score", "ethical_standards", "typical_hours", "overtime_expectations",
    "weekend_work", "flexibility_level", "leave_policy", "burnout_risk", "diversity_metrics",
    "sustainability_csr", "remote_policy_details", "carbon_footprint", "ethical_sourcing", "esg_ratings"
  ],
  Finance: [
    "annual_revenue", "annual_profit", "revenue_mix", "valuation", "profitability_status",
    "key_investors", "recent_funding_rounds", "total_capital_raised", "customer_acquisition_cost",
    "customer_lifetime_value", "cac_ltv_ratio", "churn_rate", "burn_rate", "runway_months",
    "burn_multiplier", "fixed_vs_variable_pay", "bonus_predictability", "esops_incentives"
  ],
  Growth: [
    "yoy_growth_rate", "market_share_percentage", "net_promoter_score", "customer_concentration_risk",
    "sales_motion", "tam", "sam", "som"
  ],
  Innovation: [
    "r_and_d_investment", "intellectual_property", "innovation_roadmap", "product_pipeline",
    "strategic_priorities", "benchmark_vs_peers", "future_projections"
  ],
  Locations: [
    "headquarters_address", "operating_countries", "office_count", "office_locations",
    "location_centrality", "public_transport_access", "cab_policy", "airport_commute_time",
    "office_zone_type", "area_safety", "safety_policies", "infrastructure_safety",
    "emergency_preparedness", "health_support"
  ],
  Benefits: [
    "family_health_insurance", "relocation_support", "lifestyle_benefits", "training_spend"
  ],
  Risks: [
    "supply_chain_dependencies", "geopolitical_risks", "macro_risks", "layoff_history"
  ]
};

const TABS = Object.keys(TAB_MAPPINGS);

function FieldRow({ label, value }: { label: string; value: any }) {
  if (value == null || value === "") return null;
  const strValue = Array.isArray(value) ? value.join(", ") : String(value);

  // Format label: "company_id" -> "Company Id"
  const formattedLabel = label
    .split("_")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return (
    <div className="flex flex-col sm:flex-row sm:items-start py-3 border-b border-border last:border-0 gap-1 sm:gap-4">
      <span className="text-sm font-medium text-muted-foreground w-1/3 shrink-0">{formattedLabel}</span>
      <span className="text-sm text-foreground break-words">{strValue}</span>
    </div>
  );
}

export default function CompanyDetail() {
  const { id } = useParams();
  const { data: company, isLoading } = useCompany(id);

  if (isLoading) return <div className="h-64 rounded-xl bg-surface border border-border animate-pulse" />;
  if (!company) {
    return (
      <div>
        <Link to="/companies" className="inline-flex items-center text-sm text-brand mb-4"><ArrowLeft className="h-4 w-4 mr-1" /> Back</Link>
        <EmptyState title="Company not found" description="This record is not yet available in public.company." />
      </div>
    );
  }

  return (
    <div>
      <Link to="/companies" className="inline-flex items-center text-sm text-brand mb-4 hover:underline">
        <ArrowLeft className="h-4 w-4 mr-1" /> Back to companies
      </Link>
      <PageHeader eyebrow={String(company.category ?? "Company")} title={String(company.name)} description={String(company.short_name ?? "")} />

      <Tabs defaultValue={TABS[0]} className="w-full">
        <div className="sticky top-0 lg:top-0 z-10 bg-surface-muted -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-2 border-b border-border">
          <TabsList className="bg-surface overflow-x-auto flex w-full justify-start scrollbar-thin">
            {TABS.map(t => <TabsTrigger key={t} value={t}>{t}</TabsTrigger>)}
          </TabsList>
        </div>

        {TABS.map(t => (
          <TabsContent key={t} value={t} className="mt-6">
            <div className="rounded-xl border border-border bg-surface p-6">
              <h2 className="font-display font-semibold text-lg mb-3">{t}</h2>
              <div className="flex flex-col">
                {TAB_MAPPINGS[t].map(key => (
                  <FieldRow key={key} label={key as string} value={company[key]} />
                ))}
              </div>
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
