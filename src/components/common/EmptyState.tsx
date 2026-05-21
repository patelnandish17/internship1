import { Database } from "lucide-react";
import { ReactNode } from "react";

export function EmptyState({
  icon,
  title = "No data available",
  description = "Connect the public.company table to populate this view.",
  action,
}: {
  icon?: ReactNode;
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="border border-dashed border-border rounded-xl bg-surface p-10 text-center">
      <div className="mx-auto h-12 w-12 rounded-full bg-brand-soft text-brand grid place-items-center mb-4">
        {icon ?? <Database className="h-5 w-5" />}
      </div>
      <h3 className="font-display font-semibold text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground mt-1.5 max-w-md mx-auto">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
