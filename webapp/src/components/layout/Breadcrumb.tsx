import { ChevronRight } from "lucide-react";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" className="container-page py-4">
      <ol className="flex items-center gap-1.5 text-sm text-neutral-500">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-1.5">
            {i > 0 && <ChevronRight className="w-3.5 h-3.5 text-neutral-400" />}
            {item.href ? (
              <a href={item.href} className="hover:text-primary-500 transition-colors">
                {item.label}
              </a>
            ) : (
              <span className="text-neutral-900 dark:text-white font-medium">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
