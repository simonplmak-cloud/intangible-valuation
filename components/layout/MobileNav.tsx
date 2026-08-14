"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X } from "lucide-react";

export function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setOpen(!open)}
        className="p-2 text-neutral-600 hover:text-primary-500"
        aria-label={open ? "Close menu" : "Open menu"}
      >
        {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {open && (
        <div className="absolute top-16 left-0 right-0 bg-white dark:bg-neutral-950 border-b border-neutral-200 dark:border-neutral-800 shadow-modal p-4">
          <nav className="flex flex-col gap-3">
            <Link
              href="/calculator"
              className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-neutral-100 dark:hover:bg-neutral-800"
              onClick={() => setOpen(false)}
            >
              Calculator
            </Link>
            <Link
              href="/docs"
              className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-neutral-100 dark:hover:bg-neutral-800"
              onClick={() => setOpen(false)}
            >
              Docs
            </Link>
            <Link
              href="/mcp"
              className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-neutral-100 dark:hover:bg-neutral-800"
              onClick={() => setOpen(false)}
            >
              MCP Gateway
            </Link>
            <Link
              href="/skills"
              className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-neutral-100 dark:hover:bg-neutral-800"
              onClick={() => setOpen(false)}
            >
              AI Skills
            </Link>
            <div className="border-t border-neutral-200 dark:border-neutral-800 pt-3">
              <Link
                href="/dashboard"
                className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-neutral-100 dark:hover:bg-neutral-800"
                onClick={() => setOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                href="/about"
                className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-neutral-100 dark:hover:bg-neutral-800"
                onClick={() => setOpen(false)}
              >
                About
              </Link>
            </div>
          </nav>
        </div>
      )}
    </div>
  );
}
