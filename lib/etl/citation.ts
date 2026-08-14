/**
 * Citation-chain validation for imported data.
 *
 * No seeding: every data record must carry a full citation chain
 * (source → author/date → url/doi → specific reference). Records without
 * a complete chain are rejected at import time (AC-DATA-01).
 */

export interface Citation {
  source: string;
  author: string;
  date: string;
  url?: string;
  doi?: string;
  ref: string;
}

export interface CitationError {
  field: string;
  message: string;
}

export function validateCitation(citation: Partial<Citation> | null | undefined): CitationError[] {
  const errors: CitationError[] = [];

  if (!citation) {
    return [{ field: "citation", message: "missing citation chain" }];
  }

  if (!citation.source?.trim()) errors.push({ field: "source", message: "missing source" });
  if (!citation.author?.trim()) errors.push({ field: "author", message: "missing author/publisher" });
  if (!citation.date?.trim()) errors.push({ field: "date", message: "missing publication date" });
  if (!citation.url?.trim() && !citation.doi?.trim()) {
    errors.push({ field: "url", message: "missing url or doi" });
  }
  if (!citation.ref?.trim()) errors.push({ field: "ref", message: "missing specific reference" });

  return errors;
}

export function hasValidCitation(citation: Partial<Citation> | null | undefined): boolean {
  return validateCitation(citation).length === 0;
}
