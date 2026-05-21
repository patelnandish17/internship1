import { useMemo } from "react";
import { useCompanies } from "@/hooks/useCompanies";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import {
  BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from "recharts";
import {
  PieChart as PieChartIcon,
  BarChart2,
  Briefcase,
  Activity,
  Laptop,
  Building2,
  Zap,
} from "lucide-react";

const COLORS = [
  "#6366f1", // Indigo
  "#ec4899", // Pink
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#06b6d4", // Cyan
  "#8b5cf6", // Violet
  "#f43f5e", // Rose
  "#3b82f6", // Blue
];

export default function Analytics() {
  const { data: companies = [] } = useCompanies();

  const byCategory = useMemo(() => count(companies, "category", true), [companies]);
  const byHiring = useMemo(() => count(companies, "hiring_velocity", true), [companies]);
  const byMaturity = useMemo(() => count(companies, "company_maturity", true), [companies]);
  const byAutomation = useMemo(() => count(companies, "automation_level", true), [companies]);
  const byRemotePolicy = useMemo(() => count(companies, "remote_policy_details", true), [companies]);
  const byBurnoutRisk = useMemo(() => count(companies, "burnout_risk", true), [companies]);

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        eyebrow="Analytics & Insights"
        title="Placement Dashboard"
        description="Beautiful, aggregated visual insights derived from the company intelligence dataset."
      />

      {companies.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <ChartCard 
            title="Category Distribution" 
            icon={PieChartIcon} 
            description="Breakdown of companies by primary industry category."
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={byCategory} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="40%" 
                  innerRadius={50} 
                  outerRadius={75}
                  paddingAngle={5}
                >
                  {byCategory.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={60} 
                  iconSize={10} 
                  wrapperStyle={{ fontSize: '11px', bottom: 0, lineHeight: '16px' }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard 
            title="Hiring Velocity" 
            icon={Zap}
            description="Speed and frequency of recruitment drives."
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byHiring} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: 'hsl(var(--muted) / 0.5)' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {byHiring.map((_, i) => (
                    <Cell key={i} fill={COLORS[(i + 1) % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard 
            title="Company Maturity" 
            icon={Building2}
            description="Distribution across different stages of growth."
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={byMaturity} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="40%" 
                  outerRadius={75}
                >
                  {byMaturity.map((_, i) => <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />)}
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={60} 
                  iconSize={10} 
                  wrapperStyle={{ fontSize: '11px', bottom: 0, lineHeight: '16px' }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard 
            title="Automation Level" 
            icon={Activity}
            description="Internal tooling and process automation."
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byAutomation} layout="vertical" margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} width={95} />
                <Tooltip 
                  cursor={{ fill: 'hsl(var(--muted) / 0.5)' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                  {byAutomation.map((_, i) => (
                    <Cell key={i} fill={COLORS[(i + 3) % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard 
            title="Remote Work Policy" 
            icon={Laptop}
            description="Flexibility and work-from-home culture."
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={byRemotePolicy} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="40%" 
                  innerRadius={45} 
                  outerRadius={75}
                >
                  {byRemotePolicy.map((_, i) => <Cell key={i} fill={COLORS[(i + 4) % COLORS.length]} />)}
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={75} 
                  iconSize={10} 
                  wrapperStyle={{ fontSize: '11px', bottom: 0, lineHeight: '16px' }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard 
            title="Burnout Risk" 
            icon={Briefcase}
            description="Assessed risk of employee fatigue/burnout."
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byBurnoutRisk} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: 'hsl(var(--muted) / 0.5)' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {byBurnoutRisk.map((_, i) => (
                    <Cell key={i} fill={COLORS[(i + 5) % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      )}
    </div>
  );
}

function ChartCard({ title, icon: Icon, children, description }: { title: string; icon?: React.ElementType; children: React.ReactNode; description?: string }) {
  return (
    <div className="group flex flex-col rounded-2xl border border-border/60 bg-surface/40 backdrop-blur-md p-5 shadow-sm transition-all duration-300 hover:shadow-md hover:border-brand/30">
      <div className="mb-4 flex items-start gap-3">
        {Icon && (
          <div className="rounded-lg bg-brand/10 p-2 text-brand">
            <Icon className="h-5 w-5" />
          </div>
        )}
        <div>
          <h3 className="font-display text-lg font-semibold text-foreground">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-muted-foreground mt-0.5 line-clamp-1">{description}</p>
          )}
        </div>
      </div>
      <div className="h-72 w-full mt-2">
        {children}
      </div>
    </div>
  );
}

function count(rows: any[], key: string, excludeUnknown = false) {
  const m: Record<string, number> = {};
  rows.forEach(r => {
    let val = r[key];
    if (val === null || val === undefined || val === "" || val === "N/A" || val === "-") val = "Unknown";
    const k = String(val);
    if (excludeUnknown && k.toLowerCase() === "unknown") return;
    m[k] = (m[k] ?? 0) + 1;
  });
  const entries = Object.entries(m).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
  
  if (entries.length > 7) {
    const top = entries.slice(0, 6);
    const otherVal = entries.slice(6).reduce((acc, curr) => acc + curr.value, 0);
    if (otherVal > 0) {
      top.push({ name: "Other", value: otherVal });
    }
    return top;
  }
  return entries;
}
