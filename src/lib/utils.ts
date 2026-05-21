import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function mapCategory(raw: string | null | undefined): string {
  if (!raw) return "Product Based";
  const lower = raw.toLowerCase();
  
  if (lower.includes("startup") || lower.includes("smb") || lower.includes("scale-up") || lower.includes("unicorn") || lower.includes("early stage")) {
    return "Startup or Small Scale Industries";
  }
  if (lower.includes("service") || lower.includes("consulting") || lower.includes("agency") || lower.includes("firm")) {
    return "Service Based";
  }
  if (lower.includes("giant") || lower.includes("large cap") || lower.includes("multinational") || lower.includes("conglomerate") || lower.includes("enterprise") || lower.includes("public tech") || lower.includes("global")) {
    return "Tech Giants";
  }
  
  return "Product Based";
}
