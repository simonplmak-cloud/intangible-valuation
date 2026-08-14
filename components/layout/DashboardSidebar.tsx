"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils/cn";
import { Calculator, History, Star, Download, Settings, FileText } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Saved Valuations", icon: History },
  { href: "/dashboard?filter=favorites", label: "Favorites", icon: Star },
  { href: "/dashboard?tab=export", label: "Export Reports", icon: Download },
  { href: "/dashboard?tab=settings", label: "Settings", icon: Settings },
  { href: "/calculator", label: "New Valuation", icon: Calculator },
  { href: "/docs", label: "Documentation", icon: FileText },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 hidden lg:block shrink-0">
      <nav className="sticky top-20 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                  : "text-neutral-600 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
